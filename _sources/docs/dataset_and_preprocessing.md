# Dataset and Preprocessing
We hebben eerst besloten dat elk teamlid ten minste één dataset van interesse moest vinden met voldoende gegevens waarvan ten minste twee perspectieven kunnen worden gehaald. Tijdens het eerste teamoverleg werd elke dataset besproken, samen met mogelijke correlaties. Uiteindelijk kozen we voor de datasets "World's Best Cities for People and the Planet" en "City Happiness Index 2024" van Kaggle, omdat deze datasets correlaties bevatten die nuttig kunnen zijn voor een potentieel onderwerp. Na wat brainstormen tijdens het overleg besloten we ons te verdiepen in de relatie tussen stedelijke leefbaarheid en milieuduurzaamheid, aangezien de datasets voldoende variabelen bevatten die voor twee perspectieven kunnen worden gebruikt.

# Clean Up
Elke dataset bevat verschillende kolommen en structuren. We moesten twee fasen doorlopen om alles goed te kunnen "cleanen". De eerste fase is waar kolommen worden hernoemd en hergestructureerd om ze samen te voegen. Kolommen zijn handmatig samengevoegd door ze één voor één te inspecteren en samen te voegen als ze ongeveer dezelfde naam of inhoud bevatten in termen van wat ze vertegenwoordigen. Kolommen die niet van nut waren, werden onmiddellijk uitgesloten tijdens dit proces.

De tweede fase omvat het normaliseren van de gegevens. Over het algemeen is dit gedaan door de unieke waarden voor elke kolom grondig te inspecteren en waarden die een vergelijkbare betekenis vertegenwoordigen samen te voegen.

We hebben besloten om .csv te behouden als bestandstype voor onze uiteindelijke datasets. Uiteindelijk is een totaal van talrijke kolommen verspreid over de datasets teruggebracht tot een enkele dataset met de meest relevante kolommen voor onze analyse.

# Variabele Beschrijvingen
In termen van variabel type en meetschaal kunnen de variabelen in de uiteindelijke dataset worden geclassificeerd onder verschillende combinaties:

- Continue / Ratio variabelen: Decibel-level, TrafficDensity, Hapiness-score, GreenSpaceArea
- Discrete / Ordinale variabelen: People Score, Planet Score, Profit Score, Algemene Rang, AirQualityIndex, CostofLivingIndex, Healthcare_Index
- Discrete / Nominale variabelen: Stadsnamen

# Aggregaties
Over het algemeen gebeuren de meeste aggregaties om de correlatie tussen leefbaarheid (People Score) en duurzaamheid (Planet Score) te berekenen. We analyseren ook de Geluksscore in relatie tot deze factoren. Dit omvat het berekenen van de gemiddelde scores, standaarddeviaties en correlatiecoëfficiënten om de relaties tussen deze variabelen te begrijpen.

Bijvoorbeeld, om de relatie tussen People Score en Planet Score te onderzoeken, berekenen we de correlatiecoëfficiënt. Daarnaast vergelijken we de gemiddelde "Hapiness-score" tussen verschillende continenten en analyseren we hoe deze correleert met People en Planet Scores.

# Voorbeeldanalyse
Stel dat we de relatie tussen People Score en Planet Score willen analyseren. We berekenen de gemiddelde People Score en Planet Score voor steden in verschillende continenten en vergelijken deze. Als Europese steden bijvoorbeeld een hogere gemiddelde People Score en Planet Score hebben in vergelijking met Aziatische steden, kan dit erop wijzen dat Europese steden over het algemeen leefbaarder en duurzamer zijn.

We kunnen ook de correlatie tussen BBP per hoofd van de bevolking en Geluksscore berekenen om te zien of rijkere steden de neiging hebben om gelukkigere bevolkingen te hebben. Deze veelzijdige analyse stelt ons in staat om inzichten uit meerdere perspectieven af te leiden en de complexe dynamiek tussen stedelijke leefbaarheid, duurzaamheid en geluk te begrijpen.
