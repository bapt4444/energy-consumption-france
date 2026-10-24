import json
import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Energy Consumption in France",
    page_icon=":bar_chart:",
    layout="wide"
)

st.title("Energy Consumption in France")

st.caption(
    "Exploring electricity and gas consumption across French regions (2011–2024)"
)

st.write(
    "Energy consumption varies over time and across regions. "
    "This dashboard explores how electricity and gas consumption have evolved "
    "in France between 2011 and 2024, highlighting regional differences "
    "and sector-specific patterns."
)

st.caption(
    "Data source: [Agence ORE - Annual Electricity and Gas Consumption by Region]"
    "(https://www.data.gouv.fr/datasets/consommation-annuelle-delectricite-et-gaz-par-region)"
)

st.write(
    "Use the interactive charts to explore national trends, compare regions "
    "and understand the main factors behind energy consumption."
)


# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("energy.csv")

    # Remove columns with more than 9000 missing values
    df_clean = df.dropna(axis=1, thresh=len(df) - 9000).copy()

    # Remove rows with missing consumption
    df_clean = df_clean.dropna(subset=["Conso totale (MWh)"])

    # Fill missing sectors
    df_clean["CODE GRAND SECTEUR"] = df_clean["CODE GRAND SECTEUR"].fillna("INCONNU")

    # Remove rows with zero sites
    df_clean = df_clean[df_clean["Nb sites"] > 0].copy()

    # Unit conversions
    df_clean["Conso totale (GWh)"] = df_clean["Conso totale (MWh)"] / 1000
    df_clean["Conso totale (TWh)"] = df_clean["Conso totale (MWh)"] / 1000000

    return df_clean


df = load_data()

# Load geographic data
@st.cache_data
def load_geojson():
    with open("data/regions.geojson", "r", encoding="utf-8") as f:
        return json.load(f)

regions_geo = load_geojson()

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("Evolution Filters")

    year_range = st.slider(
        "Year Range",
        min_value=int(df["Année"].min()),
        max_value=int(df["Année"].max()),
        value=(2011, 2024)
    )

    selected_regions = st.multiselect(
        "Regions",
        options=sorted(df["Nom Région"].unique()),
        default=sorted(df["Nom Région"].unique())
    )

# -----------------------------
# Filter data for evolution charts
# -----------------------------
evolution_df = df[
    (df["Année"] >= year_range[0]) &
    (df["Année"] <= year_range[1]) &
    (df["Nom Région"].isin(selected_regions))
].copy()


# -----------------------------
# Dashboard tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Evolution & Comparison",
    "Explore a Year",
    "Data Quality & Limitations",
    "Storyboard & Conclusions"
])

with tab1:
    # -----------------------------
    # Evolution over time
    # -----------------------------
    st.header("Evolution Over Time")
    st.write("How has energy consumption changed between 2011 and 2024?")

    # Charts using evolution_df
    # Total consumption by year
    annual_conso = evolution_df.groupby("Année")["Conso totale (TWh)"].sum().reset_index()
    # Total energy consumption over time
    fig = px.line(
        annual_conso,
        x="Année",
        y="Conso totale (TWh)",
        markers=True,
        title="Total Energy Consumption Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)


    # Storytelling: overall trend
    if len(annual_conso) >= 2:
        first_year = int(annual_conso["Année"].iloc[0])
        last_year = int(annual_conso["Année"].iloc[-1])

        first_value = annual_conso["Conso totale (TWh)"].iloc[0]
        last_value = annual_conso["Conso totale (TWh)"].iloc[-1]

        change = (last_value - first_value) / first_value * 100 if first_value > 0 else None

        if change is not None:
            direction = "increased" if change > 0 else "decreased"

            st.write(
                f"**Key Insight:** Between {first_year} and {last_year}, "
                f"reported energy consumption {direction} by {abs(change):.1f}%, "
                f"from {first_value:.1f} TWh to {last_value:.1f} TWh "
                "for the selected regions."
            )


    annual_conso["Yearly Change (%)"] = annual_conso["Conso totale (TWh)"].pct_change() * 100

    # Choose colors based on the change
    colors = [
        "#3B82F6" if x >= 0 else "#F59E0B"
        for x in annual_conso["Yearly Change (%)"]
    ]

    fig = px.bar(
        annual_conso,
        x="Année",
        y="Yearly Change (%)",
        title="Yearly Change in Energy Consumption"
    )

    fig.update_traces(marker_color=colors)

    fig.add_hline(y=0, line_color="black", line_width=1)

    st.plotly_chart(fig, use_container_width=True)

    # Storytelling: yearly changes
    st.write(
        "**Key Insight (France, 2011–2024):** Energy consumption is influenced "
        "by external factors such as weather conditions and economic activity. "
        "For example, the unusually warm year of 2014 reduced heating needs, "
        "while the COVID-19 pandemic in 2020 led to lower consumption "
        "as economic activity slowed down."
    )
    st.write(
        "These examples show that changes in energy consumption "
        "do not necessarily reflect long-term improvements in energy efficiency."
    )


    st.subheader("Number of Sites Over Time")

    # Total number of reported sites by year
    annual_sites = evolution_df.groupby("Année")[
        "Nb sites"
    ].sum().reset_index()

    # Evolution of the number of sites
    fig = px.line(
        annual_sites,
        x="Année",
        y="Nb sites",
        markers=True,
        title="Evolution of the Number of Reported Sites"
    )

    st.plotly_chart(fig, use_container_width=True)





    st.subheader("Electricity vs Gas")

    # Total consumption by year and energy type
    energy_conso = evolution_df.groupby(
        ["Année", "FILIERE"]
    )["Conso totale (TWh)"].sum().reset_index()

    # Electricity and gas consumption over time
    fig = px.line(
        energy_conso,
        x="Année",
        y="Conso totale (TWh)",
        color="FILIERE",
        markers=True,
        title="Electricity vs Gas Consumption"
    )

    st.plotly_chart(fig, use_container_width=True)


    # Calculate energy shares
    energy_conso["Energy Share (%)"] = (
        energy_conso["Conso totale (TWh)"] /
        energy_conso.groupby("Année")["Conso totale (TWh)"].transform("sum")
    ) * 100


    # Energy share over time
    fig = px.area(
        energy_conso,
        x="Année",
        y="Energy Share (%)",
        color="FILIERE",
        title="Electricity and Gas Share Over Time"
    )

    fig.update_layout(
        yaxis_title="Share (%)",
        yaxis_range=[0, 100]
    )

    st.plotly_chart(fig, use_container_width=True)


    # Storytelling: electricity and gas
    energy_by_year = energy_conso.pivot(
        index="Année",
        columns="FILIERE",
        values="Conso totale (TWh)"
    )

    if "Electricité" in energy_by_year and "Gaz" in energy_by_year:
        electricity_majority = energy_by_year[
            energy_by_year["Electricité"] > energy_by_year["Gaz"]
        ]

        if not electricity_majority.empty:
            first_year = int(electricity_majority.index.min())

            st.write(
                f"**Key Insight:** Electricity became the main source of "
                f"reported energy consumption in {first_year}, overtaking gas. "
                "This marks a change in the energy mix, which was previously "
                "dominated by gas."
            )

            st.write(
                "This change is mainly explained by a decrease in gas consumption, "
                "rather than a strong increase in electricity consumption. "
                "As a result, electricity represents a larger share of the total energy mix."
            )
    st.subheader("Consumption by Sector Over Time")

    # Total consumption by year and sector
    sector_evolution = evolution_df.groupby(
        ["Année", "CODE GRAND SECTEUR"]
    )["Conso totale (TWh)"].sum().reset_index()

    # Calculate sector shares
    sector_evolution["Sector Share (%)"] = (
        sector_evolution["Conso totale (TWh)"] /
        sector_evolution.groupby("Année")["Conso totale (TWh)"].transform("sum")
    ) * 100

    # Sector shares over time
    fig = px.area(
        sector_evolution,
        x="Année",
        y="Sector Share (%)",
        color="CODE GRAND SECTEUR",
        title="Energy Consumption Share by Sector Over Time"
    )

    fig.update_layout(
        yaxis_title="Share (%)",
        yaxis_range=[0, 100]
    )

    st.plotly_chart(fig, use_container_width=True)

    # Storytelling: sector distribution
    st.write(
        "**Key Insight (France, 2011–2024):** The distribution of energy consumption "
        "varies between sectors. This shows why national consumption figures "
        "are not enough to understand how energy is used in France."
    )

    st.divider()

    # -----------------------------
    # Regional comparison
    # -----------------------------
    st.header("Regional Comparison")
    st.write("Compare energy consumption between French regions.")

    # Select regions to compare
    regions_to_compare = st.multiselect(
        "Select regions to compare",
        options=sorted(df["Nom Région"].unique()),
        default=["Normandie", "Grand Est", "Hauts-de-France"]
    )

    # Total consumption by region and year
    regional_evolution = df.groupby(
        ["Année", "Nom Région"]
    )["Conso totale (TWh)"].sum().reset_index()

    # Keep selected regions and years
    regional_evolution = regional_evolution[
        (regional_evolution["Nom Région"].isin(regions_to_compare)) &
        (regional_evolution["Année"] >= year_range[0]) &
        (regional_evolution["Année"] <= year_range[1])
    ]

    # Create the regional comparison chart
    fig = px.line(
        regional_evolution,
        x="Année",
        y="Conso totale (TWh)",
        color="Nom Région",
        markers=True,
        title="Regional Energy Consumption Over Time"
    )


    # Average consumption across all 18 regions
    national_average = df.groupby("Année")["Conso totale (TWh)"].sum() / df["Nom Région"].nunique()

    national_average = national_average[
        (national_average.index >= year_range[0]) &
        (national_average.index <= year_range[1])
    ]

    # Add national regional average to the chart
    fig.add_scatter(
        x=national_average.index,
        y=national_average.values,
        mode="lines",
        name="Average per Region",
        line=dict(color="black", dash="dash")
    )


    st.plotly_chart(fig, use_container_width=True)

    # Storytelling: regional differences
    st.write(
        "**Key Insight:** Regional energy consumption varies significantly "
        "across France. Some regions consistently consume more energy than others, "
        "which may reflect differences in population, industrial activity "
        "and economic structure."
    )

    st.divider()

with tab2:
    # -----------------------------
    # Explore a specific year
    # -----------------------------
    st.header("Explore a Specific Year")





    selected_year = st.selectbox(
        "Select a year",
        options=sorted(df["Année"].unique(), reverse=True)
    )

    year_data = df[df["Année"] == selected_year].copy()

    # KPIs and charts using year_data
    # -----------------------------
    # KPI row
    # -----------------------------

    previous_year_data = df[df["Année"] == selected_year - 1]

    total = year_data["Conso totale (TWh)"].sum()
    previous_total = previous_year_data["Conso totale (TWh)"].sum()

    electricity = year_data[year_data["FILIERE"] == "Electricité"]["Conso totale (TWh)"].sum()
    previous_electricity = previous_year_data[previous_year_data["FILIERE"] == "Electricité"]["Conso totale (TWh)"].sum()

    gas = year_data[year_data["FILIERE"] == "Gaz"]["Conso totale (TWh)"].sum()
    previous_gas = previous_year_data[previous_year_data["FILIERE"] == "Gaz"]["Conso totale (TWh)"].sum()

    # Calculate yearly changes
    total_change = (total - previous_total) / previous_total * 100 if previous_total > 0 else None
    electricity_change = (electricity - previous_electricity) / previous_electricity * 100 if previous_electricity > 0 else None
    gas_change = (gas - previous_gas) / previous_gas * 100 if previous_gas > 0 else None

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Consumption",
        f"{total:.2f} TWh",
        f"{total_change:+.2f}%" if total_change is not None else None
    )

    col2.metric(
        "Electricity Consumption",
        f"{electricity:.2f} TWh",
        f"{electricity_change:+.2f}%" if electricity_change is not None else None
    )

    col3.metric(
        "Gas Consumption",
        f"{gas:.2f} TWh",
        f"{gas_change:+.2f}%" if gas_change is not None else None
    )

    st.subheader("Regional Energy Consumption")

    col1, col2 = st.columns(2)
    # Total consumption by region
    regional_total = year_data.groupby("Nom Région")[
        "Conso totale (TWh)"
    ].sum().sort_values(ascending=False).reset_index()

    # Total consumption chart
    fig = px.bar(
        regional_total,
        x="Conso totale (TWh)",
        y="Nom Région",
        orientation="h",
        title="Total Energy Consumption by Region"
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        height=650
    )

    with col1:
        st.plotly_chart(fig, use_container_width=True)


    # Average consumption per site by region
    regional_avg = year_data.groupby("Nom Région")[
        ["Conso totale (MWh)", "Nb sites"]
    ].sum()

    # Calculate average consumption per site
    regional_avg["Average per Site (MWh)"] = (
        regional_avg["Conso totale (MWh)"] / regional_avg["Nb sites"]
    )

    regional_avg = regional_avg.sort_values(
        "Average per Site (MWh)", ascending=False
    ).reset_index()

    # Average consumption chart
    fig = px.bar(
        regional_avg,
        x="Average per Site (MWh)",
        y="Nom Région",
        orientation="h",
        title="Average Energy Consumption per Site by Region"
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        height=650
    )

    with col2:
        st.plotly_chart(fig, use_container_width=True)


    # Storytelling: total vs average consumption
    st.write(
        "**Key Insight:** Regions with the highest total energy consumption "
        "do not necessarily have the highest consumption per site. "
        "This suggests that the number of sites and their energy needs "
        "both play a role in regional differences."
    )


    # Number of reported sites by region
    regional_sites = year_data.groupby("Nom Région")[
        "Nb sites"
    ].sum().sort_values(ascending=False).reset_index()

    # Number of sites chart
    fig = px.bar(
        regional_sites,
        x="Nb sites",
        y="Nom Région",
        orientation="h",
        title=f"Number of Reported Sites by Region in {selected_year}"
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sector Distribution by Region")

    # Total consumption by region and sector
    regional_sectors = year_data.groupby(
        ["Nom Région", "CODE GRAND SECTEUR"]
    )["Conso totale (TWh)"].sum().reset_index()

    # Calculate sector shares for each region
    regional_sectors["Sector Share (%)"] = (
        regional_sectors["Conso totale (TWh)"] /
        regional_sectors.groupby("Nom Région")["Conso totale (TWh)"].transform("sum")
    ) * 100

    # Sector distribution chart
    fig = px.bar(
        regional_sectors,
        x="Sector Share (%)",
        y="Nom Région",
        color="CODE GRAND SECTEUR",
        orientation="h",
        title=f"Energy Consumption by Sector and Region in {selected_year}"
    )

    fig.update_layout(
        barmode="stack",
        xaxis_title="Share (%)",
        xaxis_range=[0, 100],
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)


    # Storytelling: regional sector differences
    st.write(
        "**Key Insight:** The energy mix by sector differs across French regions. "
        "Some regions have a larger industrial share, while others have "
        "a stronger residential or tertiary share. "
        "These differences help explain why regional energy consumption "
        "cannot be compared using total values alone."
    )

    st.subheader("Energy Consumption Map")

    # Total consumption by region
    regional_map = year_data.groupby(
        ["Code Région", "Nom Région"]
    )["Conso totale (TWh)"].sum().reset_index()

    # Format region codes
    regional_map["Code Région"] = (
        regional_map["Code Région"].astype(str).str.zfill(2)
    )

    # Overseas region codes
    overseas_codes = ["01", "02", "03", "04", "06"]

    # Metropolitan regions
    metro_map = regional_map[
        ~regional_map["Code Région"].isin(overseas_codes)
    ]

    # Metropolitan France map
    fig = px.choropleth(
        metro_map,
        geojson=regions_geo,
        locations="Code Région",
        featureidkey="properties.code",
        color="Conso totale (TWh)",
        hover_name="Nom Région",
        color_continuous_scale="Viridis",
        range_color=(0, regional_map["Conso totale (TWh)"].max()),
        title=f"Metropolitan France - {selected_year}"
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(height=550)

    st.plotly_chart(fig, use_container_width=True)

    st.write("**Overseas Regions**")

    # Overseas regions
    overseas_regions = {
        "01": "Guadeloupe",
        "02": "Martinique",
        "03": "Guyane",
        "04": "La Réunion",
        "06": "Mayotte"
    }

    cols = st.columns(5)

    for i, (code, name) in enumerate(overseas_regions.items()):

        # Select one overseas region
        region = regional_map[
            regional_map["Code Région"] == code
        ]

        # Create a small map
        fig = px.choropleth(
            region,
            geojson=regions_geo,
            locations="Code Région",
            featureidkey="properties.code",
            color="Conso totale (TWh)",
            hover_name="Nom Région",
            color_continuous_scale="Viridis",
            range_color=(0, regional_map["Conso totale (TWh)"].max())
        )

        fig.update_geos(
            fitbounds="locations",
            visible=False
        )

        fig.update_layout(
            height=220,
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_showscale=False
        )

        with cols[i]:
            st.write(f"**{name}**")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -----------------------------
    # Regional Deep Dive
    # -----------------------------
    st.subheader("Regional Deep Dive")
    st.write("Compare a selected region with the rest of France.")

    # Select a region
    selected_region = st.selectbox(
        "Select a region",
        options=sorted(df["Nom Région"].unique())
    )

    # Data for the selected region and year
    region_data = year_data[
        year_data["Nom Région"] == selected_region
    ].copy()

    # Data for the previous year
    previous_region_data = df[
        (df["Nom Région"] == selected_region) &
        (df["Année"] == selected_year - 1)
    ].copy()


    # Regional consumption
    region_total = region_data["Conso totale (TWh)"].sum()
    region_electricity = region_data[
        region_data["FILIERE"] == "Electricité"
    ]["Conso totale (TWh)"].sum()
    region_gas = region_data[
        region_data["FILIERE"] == "Gaz"
    ]["Conso totale (TWh)"].sum()

    # Previous year consumption
    previous_region_total = previous_region_data["Conso totale (TWh)"].sum()
    previous_region_electricity = previous_region_data[
        previous_region_data["FILIERE"] == "Electricité"
    ]["Conso totale (TWh)"].sum()
    previous_region_gas = previous_region_data[
        previous_region_data["FILIERE"] == "Gaz"
    ]["Conso totale (TWh)"].sum()

    # Average consumption per site
    region_avg_site = (
        region_data["Conso totale (MWh)"].sum() /
        region_data["Nb sites"].sum()
    )

    previous_region_avg_site = (
        previous_region_data["Conso totale (MWh)"].sum() /
        previous_region_data["Nb sites"].sum()
        if previous_region_data["Nb sites"].sum() > 0 else None
    )


    # Total consumption for each region
    regional_totals = year_data.groupby("Nom Région")[
        "Conso totale (TWh)"
    ].sum()

    # Regional mean and median
    regional_mean = regional_totals.mean()
    regional_median = regional_totals.median()

    # Previous year regional totals
    previous_regional_totals = previous_year_data.groupby("Nom Région")[
        "Conso totale (TWh)"
    ].sum()

    previous_mean = previous_regional_totals.mean()
    previous_median = previous_regional_totals.median()

    # National share
    national_share = region_total / total * 100
    previous_national_share = (
        previous_region_total / previous_total * 100
        if previous_total > 0 else None
    )

    # Calculate percentage change
    def pct_change(current, previous):
        if previous is None or pd.isna(previous) or previous == 0:
            return None
        return (current - previous) / previous * 100

    # Yearly changes
    region_total_change = pct_change(region_total, previous_region_total)
    mean_change = pct_change(regional_mean, previous_mean)
    median_change = pct_change(regional_median, previous_median)
    region_avg_change = pct_change(region_avg_site, previous_region_avg_site)

    # National share change in percentage points
    share_change = (
        national_share - previous_national_share
        if previous_national_share is not None else None
    )

    st.write("**Regional Consumption Comparison**")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Selected Region",
        f"{region_total:.2f} TWh",
        f"{region_total_change:+.2f}%" if region_total_change is not None else None,
        delta_color="off"
    )

    col2.metric(
        "Regional Mean",
        f"{regional_mean:.2f} TWh",
        f"{mean_change:+.2f}%" if mean_change is not None else None,
        delta_color="off"
    )

    col3.metric(
        "Regional Median",
        f"{regional_median:.2f} TWh",
        f"{median_change:+.2f}%" if median_change is not None else None,
        delta_color="off"
    )


    st.write("**Regional Indicators**")

    col1, col2 = st.columns(2)

    col1.metric(
        "National Share",
        f"{national_share:.2f}%",
        f"{share_change:+.2f} pp" if share_change is not None else None,
        delta_color="off"
    )

    col2.metric(
        "Average Consumption per Site",
        f"{region_avg_site:.2f} MWh",
        f"{region_avg_change:+.2f}%" if region_avg_change is not None else None,
        delta_color="off"
    )

    st.subheader("Electricity vs Gas Comparison")

    # National consumption by energy type
    national_energy = year_data.groupby("FILIERE")[
        "Conso totale (TWh)"
    ].sum().reset_index()

    # Regional consumption by energy type
    regional_energy = region_data.groupby("FILIERE")[
        "Conso totale (TWh)"
    ].sum().reset_index()

    # Display charts side by side
    col1, col2 = st.columns(2)

    # National energy mix
    fig = px.pie(
        national_energy,
        names="FILIERE",
        values="Conso totale (TWh)",
        hole=0.5,
        title=f"France - {selected_year}",
        color="FILIERE",
        color_discrete_map={
            "Electricité": "#3B82F6",
            "Gaz": "#F59E0B"
        }
    )

    fig.update_traces(textinfo="percent+label")

    with col1:
        st.plotly_chart(fig, use_container_width=True)


    # Regional energy mix
    fig = px.pie(
        regional_energy,
        names="FILIERE",
        values="Conso totale (TWh)",
        hole=0.5,
        title=f"{selected_region} - {selected_year}",
        color="FILIERE",
        color_discrete_map={
            "Electricité": "#3B82F6",
            "Gaz": "#F59E0B"
        }
    )

    fig.update_traces(textinfo="percent+label")

    with col2:
        st.plotly_chart(fig, use_container_width=True)

    # Warn about missing energy types
    if len(regional_energy) < 2:
        st.info(
            "Only one energy type is available for this region and year. "
            "The chart shows the distribution of available data only."
        )

    st.subheader("Sector Comparison: France vs Region")

    # National consumption by sector
    national_sectors = year_data.groupby("CODE GRAND SECTEUR")[
        "Conso totale (TWh)"
    ].sum().reset_index()

    # Regional consumption by sector
    region_sectors = region_data.groupby("CODE GRAND SECTEUR")[
        "Conso totale (TWh)"
    ].sum().reset_index()

    # Calculate percentages
    national_sectors["France (%)"] = (
        national_sectors["Conso totale (TWh)"] /
        national_sectors["Conso totale (TWh)"].sum() * 100
    )

    region_sectors["Region (%)"] = (
        region_sectors["Conso totale (TWh)"] /
        region_sectors["Conso totale (TWh)"].sum() * 100
    )

    # Combine national and regional shares
    sector_comparison = pd.merge(
        national_sectors[["CODE GRAND SECTEUR", "France (%)"]],
        region_sectors[["CODE GRAND SECTEUR", "Region (%)"]],
        on="CODE GRAND SECTEUR",
        how="outer"
    ).fillna(0)

    # Compare sector shares
    fig = px.bar(
        sector_comparison,
        x="CODE GRAND SECTEUR",
        y=["France (%)", "Region (%)"],
        barmode="group",
        title=f"Sector Distribution: France vs {selected_region} ({selected_year})"
    )

    fig.update_layout(
        xaxis_title="Sector",
        yaxis_title="Share (%)",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)



    # Storytelling: regional sector comparison
    st.write(
        f"**Key Insight:** {selected_region} does not necessarily have "
        "the same sector distribution as France overall. "
        "Comparing sector shares helps identify which activities "
        "are more or less represented in the selected region."
    )

with tab3:
    # -----------------------------
    # Data Quality & Limitations
    # -----------------------------
    st.header("Data Quality & Limitations")
    st.write("Explore the data cleaning process and quality checks.")

    st.write(
        "Before analyzing energy consumption, the dataset was cleaned "
        "to remove incomplete or invalid observations. "
        "The following checks summarize the cleaning process and the quality of the remaining data."
    )

    # Load original data
    raw_df = pd.read_csv("energy.csv")

    # Dataset size
    original_rows = len(raw_df)
    cleaned_rows = len(df)
    removed_rows = original_rows - cleaned_rows

    # Quality KPIs
    col1, col2, col3 = st.columns(3)

    col1.metric("Original Rows", f"{original_rows:,}")
    col2.metric("Removed Rows", f"{removed_rows:,}")
    col3.metric("Cleaned Rows", f"{cleaned_rows:,}")

    st.subheader("Removed Columns")

    # Columns removed during cleaning
    removed_columns = raw_df.columns.difference(df.columns)

    # Missing values in removed columns
    removed_summary = pd.DataFrame({
        "Column": removed_columns,
        "Missing Values": raw_df[removed_columns].isna().sum().values
    })

    # Calculate missing percentages
    removed_summary["Missing (%)"] = (
        removed_summary["Missing Values"] / len(raw_df) * 100
    )

    st.dataframe(removed_summary, use_container_width=True)


    st.write(
        "Columns with more than 9,000 missing values were removed. "
        "Other columns were kept when they contained enough information "
        "for the analysis."
    )


    st.subheader("Data Cleaning")

    # Missing consumption
    missing_consumption = raw_df["Conso totale (MWh)"].isna().sum()

    # Invalid sites after removing missing consumption
    valid_consumption = raw_df.dropna(subset=["Conso totale (MWh)"])
    invalid_sites = (valid_consumption["Nb sites"] <= 0).sum()

    # Cleaning summary
    cleaning_summary = pd.DataFrame({
        "Reason": ["Missing Consumption", "Zero or Negative Sites"],
        "Rows Removed": [missing_consumption, invalid_sites]
    })

    st.dataframe(cleaning_summary, use_container_width=True, hide_index=True)

    st.write(
        f"A total of {removed_rows:,} rows were removed during cleaning. "
        "Rows with missing energy consumption could not be used in the analysis. "
        "Rows with zero or negative sites were also removed to ensure valid "
        "consumption-per-site calculations."
    )


    st.subheader("Data Validation")

    # Quality checks
    duplicates = df.duplicated().sum()
    negative_consumption = (df["Conso totale (MWh)"] < 0).sum()
    invalid_sites_clean = (df["Nb sites"] <= 0).sum()

    # Validation summary
    validation_summary = pd.DataFrame({
        "Check": [
            "Duplicate Rows",
            "Negative Consumption",
            "Zero or Negative Sites"
        ],
        "Issues Found": [
            duplicates,
            negative_consumption,
            invalid_sites_clean
        ]
    })

    st.dataframe(validation_summary, use_container_width=True)

    st.write(
        "The cleaned dataset was checked for duplicate rows, "
        "negative consumption values and invalid site counts. "
        "These checks help identify inconsistencies that could affect the results."
    )

    st.subheader("Remaining Missing Values")

    # Missing values in cleaned data
    missing_values = df.isna().sum().reset_index()
    missing_values.columns = ["Column", "Missing Values"]

    # Keep only columns with missing values
    missing_values = missing_values[
        missing_values["Missing Values"] > 0
    ].sort_values("Missing Values", ascending=False)

    if missing_values.empty:
        st.success("No missing values in the cleaned dataset.")
    else:
        st.dataframe(missing_values, use_container_width=True)

    st.write(
        "Some missing values were kept when they did not prevent the analysis. "
        "Missing sector information was classified as 'INCONNU' "
        "instead of removing the corresponding observations."
    )

    st.subheader("Data Limitations")

    st.write(
        """
        - The dataset covers electricity and gas consumption from 2011 to 2024.
        - Some regions and years may have incomplete data.
        - Missing energy types should not be interpreted as zero consumption.
        - The number of reported sites may not represent unique physical sites.
        - Regional comparisons are not adjusted for population or economic activity.
        - Changes in consumption do not necessarily indicate changes in energy efficiency.
        """
    )


with tab4:
    # -----------------------------
    # Key Insights & Conclusions
    # -----------------------------
    st.header("Storyboard & Conclusions")


    st.write(
        "This storyboard summarizes the main steps of the analysis, "
        "from the evolution of energy consumption to regional differences "
        "and the key conclusions."
    )

    st.markdown(
        "**Main Question:** How has energy consumption changed in France "
        "between 2011 and 2024, and how do regional patterns differ?"
    )

    st.write(
        "This dashboard explored how electricity and gas consumption "
        "changed across French regions between 2011 and 2024."
    )

    st.subheader("1. Overall Consumption Trend")

    st.write(
        "Total reported energy consumption decreased between 2011 and 2024, "
        "but the decline was not regular. For example, the warm weather in "
        "2014 and the COVID-19 pandemic in 2020 help explain some of the "
        "larger changes observed."
    )

    st.subheader("2. Electricity and Gas")

    st.write(
        "Gas consumption decreased over the period, while electricity "
        "became the largest source of reported energy consumption in 2023. "
        "This shows an important change in the balance between the two energies."
    )

    st.subheader("3. Regional Differences")

    st.write(
        "Energy consumption varies significantly between French regions. "
        "Regions with high total consumption do not necessarily have "
        "the highest consumption per site."
    )

    st.subheader("4. Sector Distribution")

    st.write(
        "The distribution of energy consumption across sectors differs "
        "between regions. Industrial, residential and tertiary activities "
        "do not have the same importance everywhere."
    )

    st.subheader("5. Limitations")

    st.write(
        "The results should be interpreted carefully because some data "
        "may be missing and regional consumption is influenced by factors "
        "such as population, weather and economic activity."
    )

    st.subheader("Next Steps")

    st.write(
        "Further analysis could combine energy consumption with population, "
        "temperature and economic data to better understand regional "
        "differences and changes over time."
    )