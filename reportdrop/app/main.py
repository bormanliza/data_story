import json
import os

import stripe
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends, UploadFile, File, Form, Header
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from .models import init_db, get_db, Report, User
from .auth import (
    create_user, authenticate_user, set_session,
    get_current_user, require_login,
)
from .reports import parse_csv, build_report_context

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
FREE_REPORT_LIMIT = 3

app = FastAPI(title="ReportDrop")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "dev-secret-key"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.on_event("startup")
def startup():
    init_db()


# --- Landing ---

@app.get("/", response_class=HTMLResponse)
def landing(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("landing.html", {"request": request})


# --- Auth ---

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request, "mode": "register"})


@app.post("/register")
def register(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    try:
        user = create_user(db, email, password)
    except ValueError as e:
        return templates.TemplateResponse("auth.html", {
            "request": request, "mode": "register", "error": str(e),
        })
    set_session(request, user.id)
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request, "mode": "login"})


@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse("auth.html", {
            "request": request, "mode": "login", "error": "Invalid email or password",
        })
    set_session(request, user.id)
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


# --- Dashboard ---

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = require_login(request, db)
    reports = db.query(Report).filter(Report.user_id == user.id).order_by(Report.created_at.desc()).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "user": user, "reports": reports,
    })


# --- Upload ---

@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, db: Session = Depends(get_db)):
    user = require_login(request, db)
    return templates.TemplateResponse("upload.html", {"request": request, "user": user})


@app.post("/upload")
async def upload_csv(
    request: Request,
    title: str = Form(...),
    template_type: str = Form("general"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = require_login(request, db)
    report_count = db.query(Report).filter(Report.user_id == user.id).count()
    if not user.is_subscribed and report_count >= FREE_REPORT_LIMIT:
        return templates.TemplateResponse("upload.html", {
            "request": request, "user": user,
            "error": f"Free plan limited to {FREE_REPORT_LIMIT} reports. Upgrade to Pro for unlimited reports.",
        })
    contents = await file.read()
    data = parse_csv(contents, file.filename)
    report = Report(
        user_id=user.id,
        title=title,
        data_json=json.dumps(data),
        template_type=template_type,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return RedirectResponse(f"/report/{report.public_slug}", status_code=303)


# --- Report View ---

@app.get("/report/{slug}", response_class=HTMLResponse)
def view_report(slug: str, request: Request, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.public_slug == slug).first()
    if not report:
        return HTMLResponse("<h1>Report not found</h1>", status_code=404)
    context = build_report_context(report.data_json, report.template_type)
    template_name = f"report_templates/{report.template_type}.html"
    return templates.TemplateResponse(template_name, {
        "request": request,
        "report": report,
        **context,
    })


# --- Delete Report ---

# --- Stripe ---

@app.get("/billing", response_class=HTMLResponse)
def billing_page(request: Request, db: Session = Depends(get_db)):
    user = require_login(request, db)
    return templates.TemplateResponse("billing.html", {"request": request, "user": user})


@app.post("/create-checkout-session")
def create_checkout_session(request: Request, db: Session = Depends(get_db)):
    user = require_login(request, db)
    if not STRIPE_PRICE_ID:
        return JSONResponse({"error": "Stripe not configured"}, status_code=500)
    session = stripe.checkout.Session.create(
        customer_email=user.email,
        payment_method_types=["card"],
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
        mode="subscription",
        success_url=f"{BASE_URL}/billing?success=1",
        cancel_url=f"{BASE_URL}/billing?canceled=1",
        metadata={"user_id": user.id},
    )
    return RedirectResponse(session.url, status_code=303)


@app.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return JSONResponse({"error": "Invalid signature"}, status_code=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_subscribed = True
                user.stripe_customer_id = session.get("customer")
                db.commit()

    if event["type"] == "customer.subscription.deleted":
        customer_id = event["data"]["object"].get("customer")
        if customer_id:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if user:
                user.is_subscribed = False
                db.commit()

    return JSONResponse({"status": "ok"})


# --- Delete Report ---

@app.post("/report/{slug}/delete")
def delete_report(slug: str, request: Request, db: Session = Depends(get_db)):
    user = require_login(request, db)
    report = db.query(Report).filter(Report.public_slug == slug, Report.user_id == user.id).first()
    if report:
        db.delete(report)
        db.commit()
    return RedirectResponse("/dashboard", status_code=303)
