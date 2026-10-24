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

Some data may be missing for particular regions or energy types. Regional consumption is not adjusted for population or economic activity, and changes in consumption do not necessarily mean changes in energy efficiency.

Also, not all available data was used, such as detailed sector codes and energy operators.

Future improvements could include these variables, as well as population, temperature and economic data, to better explain regional differences.


## Technologies

Python, Pandas, Plotly and Streamlit.

## Project Links

- [Streamlit App](https://energy-consumption-france.streamlit.app/)
- [GitHub Repository](https://github.com/bapt4444/energy-consumption-france)
- [Demo Video](https://efrei365net-my.sharepoint.com/:v:/g/personal/baptiste_bertrand_20231493_efrei_net/IQBVm9SNhV13QapLYpQ5sytjAYSMa2W2MV2rNch7Fo6ZviA?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=z9Z2z1)