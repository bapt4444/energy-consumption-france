# Energy Consumption in France

## Project Overview

This project is an interactive Streamlit dashboard analyzing electricity and gas consumption across French regions between 2011 and 2024.

The main objective is to explore energy consumption trends, compare regional differences, and understand how consumption varies between sectors.

## Dataset

**Source:** Agence ORE — Annual Electricity and Gas Consumption by Region

Dataset: https://www.data.gouv.fr/datasets/consommation-annuelle-delectricite-et-gaz-par-region

The dataset includes annual energy consumption, energy types, regions, sectors and the number of reported sites.

## Data Cleaning

The dataset was cleaned using Python and Pandas:

- Removed columns with more than 9,000 missing values.
- Removed rows with missing energy consumption.
- Removed rows with zero or negative site counts.
- Replaced missing sector codes with `INCONNU`.
- Converted energy consumption from MWh to GWh and TWh.
- Checked for duplicates and invalid values.

The original dataset contained 33,502 rows, and 33,083 rows were kept after cleaning.

## Dashboard Features

The dashboard contains four sections:

1. **Evolution & Comparison:** National trends, electricity versus gas, sector evolution and regional comparisons.
2. **Explore a Year:** Regional rankings, interactive maps, KPIs and regional deep dives.
3. **Data Quality & Limitations:** Data cleaning, missing values and validation checks.
4. **Storyboard & Conclusions:** Main findings, interpretations, limitations and next steps.

## Installation

Install the required libraries:

```bash
pip install -r requirements.txt
```

Launch the application:

```bash
streamlit run project_app.py
```

## Main Findings

- Reported energy consumption decreased overall between 2011 and 2024.
- Electricity overtook gas consumption in 2023 in the national dataset.
- Regional consumption varies depending on the number of sites and their consumption levels.
- Sector distributions differ between regions.
- Weather and economic events can help explain some annual variations.

## Limitations

Some data may be missing for particular regions or energy types. Regional consumption figures are not adjusted for population or economic activity, and the observed changes do not necessarily indicate changes in energy efficiency.

## Technologies

Python, Pandas, Plotly and Streamlit.