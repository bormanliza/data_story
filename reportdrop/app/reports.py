import json
import io
from typing import List

import pandas as pd
import plotly.express as px
import plotly.io as pio


def parse_csv(file_bytes: bytes, filename: str) -> dict:
    """Parse uploaded CSV and return structured data for report generation."""
    for sep in [",", ";", "\t"]:
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), sep=sep)
            if len(df.columns) > 1:
                break
        except Exception:
            continue
    else:
        df = pd.read_csv(io.BytesIO(file_bytes))

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = []
    for col in categorical_cols[:]:
        try:
            pd.to_datetime(df[col])
            date_cols.append(col)
            categorical_cols.remove(col)
        except (ValueError, TypeError):
            pass

    summary = {}
    for col in numeric_cols:
        desc = df[col].describe()
        summary[col] = {k: round(float(v), 2) for k, v in desc.items()}

    return {
        "filename": filename,
        "rows": len(df),
        "columns": list(df.columns),
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "date_cols": date_cols,
        "summary": summary,
        "preview": df.head(20).to_dict(orient="records"),
        "full_data": df.to_dict(orient="records"),
    }


def generate_charts(data: dict) -> List[dict]:
    """Generate Plotly chart HTML snippets from parsed data."""
    charts = []
    df = pd.DataFrame(data["full_data"])
    numeric_cols = data["numeric_cols"]
    categorical_cols = data["categorical_cols"]
    date_cols = data["date_cols"]

    # Bar chart: first categorical vs first numeric
    if categorical_cols and numeric_cols:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        top_values = df[cat_col].value_counts().head(15).index.tolist()
        chart_df = df[df[cat_col].isin(top_values)]
        fig = px.bar(
            chart_df.groupby(cat_col)[num_col].mean().reset_index(),
            x=cat_col, y=num_col,
            title=f"Average {num_col} by {cat_col}",
            color_discrete_sequence=["#6366f1"],
        )
        fig.update_layout(template="plotly_white")
        charts.append({
            "title": f"Average {num_col} by {cat_col}",
            "html": pio.to_html(fig, full_html=False, include_plotlyjs=False),
        })

    # Line chart if date column exists
    if date_cols and numeric_cols:
        date_col = date_cols[0]
        num_col = numeric_cols[0]
        line_df = df.copy()
        line_df[date_col] = pd.to_datetime(line_df[date_col])
        line_df = line_df.sort_values(date_col)
        fig = px.line(
            line_df, x=date_col, y=num_col,
            title=f"{num_col} over time",
            color_discrete_sequence=["#8b5cf6"],
        )
        fig.update_layout(template="plotly_white")
        charts.append({
            "title": f"{num_col} over time",
            "html": pio.to_html(fig, full_html=False, include_plotlyjs=False),
        })

    # Distribution histogram for numeric columns
    for col in numeric_cols[:2]:
        fig = px.histogram(
            df, x=col,
            title=f"Distribution of {col}",
            color_discrete_sequence=["#a78bfa"],
            nbins=30,
        )
        fig.update_layout(template="plotly_white")
        charts.append({
            "title": f"Distribution of {col}",
            "html": pio.to_html(fig, full_html=False, include_plotlyjs=False),
        })

    # Pie chart if categorical column exists
    if categorical_cols:
        cat_col = categorical_cols[0]
        value_counts = df[cat_col].value_counts().head(8)
        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=f"Distribution of {cat_col}",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        charts.append({
            "title": f"Distribution of {cat_col}",
            "html": pio.to_html(fig, full_html=False, include_plotlyjs=False),
        })

    return charts


def build_report_context(data_json: str, template_type: str) -> dict:
    """Build full report context for template rendering."""
    data = json.loads(data_json)
    charts = generate_charts(data)
    return {
        "data": data,
        "charts": charts,
        "template_type": template_type,
        "summary": data.get("summary", {}),
        "preview": data.get("preview", []),
        "columns": data.get("columns", []),
        "row_count": data.get("rows", 0),
    }
