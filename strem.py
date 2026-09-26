import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="HHS Data Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# -------------------------------------------------
# TITLE
# -------------------------------------------------

st.title("📊 HHS Data Analysis & Forecasting Dashboard")

st.markdown(
    """
    This application analyzes HHS care load, system pressure,
    trends, backlog indicators and future care-load forecasts.
    """
)

# -----------------------------
# LOAD DATA
# -----------------------------

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "rebuild.csv"

if not DATA_FILE.exists():
    st.error("rebuild.csv file nahi mili!")
    st.stop()

df = pd.read_csv(DATA_FILE)

st.success("rebuild.csv automatically loaded successfully!")

# -------------------------------------------------
# COLUMN CLEANING
# -------------------------------------------------

df.columns = df.columns.str.strip()
# Rename dataset columns to match dashboard names
df = df.rename(columns={
    "CBP custody": "CBP Custody",
    "transferred": "Transfers",
    "discharge": "Discharges"
})

# Change this if your actual date column has another name
DATE_COLUMN = "Date"

if DATE_COLUMN not in df.columns:
    st.error(
        f"'{DATE_COLUMN}' column not found. "
        f"Available columns: {list(df.columns)}"
    )
    st.stop()

df[DATE_COLUMN] = pd.to_datetime(
    df[DATE_COLUMN],
    errors="coerce"
)

df = df.dropna(subset=[DATE_COLUMN])

df = df.sort_values(DATE_COLUMN)

# -------------------------------------------------
# SIDEBAR FILTER
# -------------------------------------------------

st.sidebar.header("Filters")

min_date = df[DATE_COLUMN].min().date()
max_date = df[DATE_COLUMN].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    filtered_df = df[
        (df[DATE_COLUMN] >= start_date) &
        (df[DATE_COLUMN] <= end_date)
    ].copy()

else:
    filtered_df = df.copy()

# -------------------------------------------------
# REQUIRED COLUMNS
# -------------------------------------------------

HHS_COLUMN = "Children in HHS Care"
CBP_COLUMN = "CBP Custody"
TRANSFER_COLUMN = "Transfers"
DISCHARGE_COLUMN = "Discharges"

# Check available columns

required_columns = [
    HHS_COLUMN,
    CBP_COLUMN,
    TRANSFER_COLUMN,
    DISCHARGE_COLUMN
]

missing_columns = [
    col for col in required_columns
    if col not in filtered_df.columns
]

if missing_columns:

    st.error(
        "These columns are missing from your dataset: "
        + ", ".join(missing_columns)
    )

    st.write("Available columns:")
    st.write(list(filtered_df.columns))

    st.stop()

# -------------------------------------------------
# NUMERIC CONVERSION
# -------------------------------------------------

for col in required_columns:

    filtered_df[col] = pd.to_numeric(
        filtered_df[col],
        errors="coerce"
    )

# -------------------------------------------------
# DERIVED METRICS
# -------------------------------------------------

# Total System Load
filtered_df["Total System Load"] = (
    filtered_df[CBP_COLUMN]
    + filtered_df[HHS_COLUMN]
)

# Net Daily Intake
filtered_df["Net Daily Intake"] = (
    filtered_df[TRANSFER_COLUMN]
    - filtered_df[DISCHARGE_COLUMN]
)

# Day-over-day Growth Rate
filtered_df["Care Load Growth Rate"] = (
    filtered_df[HHS_COLUMN]
    .pct_change()
    * 100
)

# Rolling averages
filtered_df["7-Day Average"] = (
    filtered_df[HHS_COLUMN]
    .rolling(7)
    .mean()
)

filtered_df["14-Day Average"] = (
    filtered_df[HHS_COLUMN]
    .rolling(14)
    .mean()
)

# -------------------------------------------------
# BACKLOG INDICATOR
# -------------------------------------------------

filtered_df["Backlog Indicator"] = (
    filtered_df["Net Daily Intake"]
    .rolling(7)
    .mean()
)

# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------

st.header("📌 KPI Summary")

col1, col2, col3, col4 = st.columns(4)

current_hhs = filtered_df[HHS_COLUMN].iloc[-1]

average_hhs = filtered_df[HHS_COLUMN].mean()

max_hhs = filtered_df[HHS_COLUMN].max()

avg_net_intake = filtered_df["Net Daily Intake"].mean()

col1.metric(
    "Current HHS Care",
    f"{current_hhs:,.0f}"
)

col2.metric(
    "Average HHS Care",
    f"{average_hhs:,.0f}"
)

col3.metric(
    "Maximum HHS Care",
    f"{max_hhs:,.0f}"
)

col4.metric(
    "Average Net Intake",
    f"{avg_net_intake:,.2f}"
)

# -------------------------------------------------
# SYSTEM LOAD
# -------------------------------------------------

st.header("🏥 System Load Overview")

fig_system = px.line(
    filtered_df,
    x=DATE_COLUMN,
    y=["Total System Load", HHS_COLUMN, CBP_COLUMN],
    title="Total System Load, HHS Care and CBP Custody"
)

st.plotly_chart(
    fig_system,
    use_container_width=True
)

# -------------------------------------------------
# HHS CARE TREND
# -------------------------------------------------

st.header("📈 HHS Care Trend")

fig_hhs = px.line(
    filtered_df,
    x=DATE_COLUMN,
    y=HHS_COLUMN,
    title="Daily HHS Care Load"
)

st.plotly_chart(
    fig_hhs,
    use_container_width=True
)

# -------------------------------------------------
# ROLLING AVERAGE
# -------------------------------------------------

st.header("🔄 Rolling Average Analysis")

fig_rolling = px.line(
    filtered_df,
    x=DATE_COLUMN,
    y=[
        HHS_COLUMN,
        "7-Day Average",
        "14-Day Average"
    ],
    title="HHS Care with 7-Day and 14-Day Rolling Average"
)

st.plotly_chart(
    fig_rolling,
    use_container_width=True
)

# -------------------------------------------------
# NET INTAKE
# -------------------------------------------------

st.header("📊 Net Intake & Backlog Trend")

fig_net = px.line(
    filtered_df,
    x=DATE_COLUMN,
    y="Net Daily Intake",
    title="Net Daily Intake"
)

fig_net.add_hline(
    y=0,
    line_dash="dash"
)

st.plotly_chart(
    fig_net,
    use_container_width=True
)

# -------------------------------------------------
# GROWTH RATE
# -------------------------------------------------

st.header("📈 Care Load Growth Rate")

fig_growth = px.line(
    filtered_df,
    x=DATE_COLUMN,
    y="Care Load Growth Rate",
    title="Day-over-Day HHS Care Growth Rate"
)

st.plotly_chart(
    fig_growth,
    use_container_width=True
)

# -------------------------------------------------
# FORECAST
# -------------------------------------------------

st.header("🔮 HHS Care Forecast")

st.info(
    "This section provides a simple trend-based forecast "
    "using historical HHS Care values."
)

forecast_days = st.slider(
    "Forecast Period (Days)",
    min_value=7,
    max_value=180,
    value=30
)

# Historical values
history = filtered_df[
    [DATE_COLUMN, HHS_COLUMN]
].dropna()

if len(history) >= 14:

    # Use last 30 observations
    recent = history.tail(30)

    x = np.arange(len(recent))

    y = recent[HHS_COLUMN].values

    # Linear trend
    coefficients = np.polyfit(
        x,
        y,
        1
    )

    trend = np.poly1d(coefficients)

    future_x = np.arange(
        len(recent),
        len(recent) + forecast_days
    )

    future_values = trend(future_x)

    future_dates = pd.date_range(
        start=recent[DATE_COLUMN].iloc[-1]
        + pd.Timedelta(days=1),
        periods=forecast_days,
        freq="D"
    )

    forecast_df = pd.DataFrame({

        DATE_COLUMN: future_dates,

        HHS_COLUMN: future_values

    })

    # Historical + forecast
    historical_plot = recent.copy()

    historical_plot["Type"] = "Historical"

    forecast_df["Type"] = "Forecast"

    combined = pd.concat(
        [
            historical_plot,
            forecast_df
        ],
        ignore_index=True
    )

    fig_forecast = px.line(
        combined,
        x=DATE_COLUMN,
        y=HHS_COLUMN,
        color="Type",
        title="HHS Care Load: Historical vs Forecast"
    )

    st.plotly_chart(
        fig_forecast,
        use_container_width=True
    )

    # Forecast table

    st.subheader("Forecast Values")

    st.dataframe(
        forecast_df,
        use_container_width=True
    )

else:

    st.warning(
        "Not enough historical data available for forecasting."
    )

# -------------------------------------------------
# DATA QUALITY
# -------------------------------------------------

st.header("🔍 Data Quality & Validation")

quality_col1, quality_col2, quality_col3 = st.columns(3)

missing_dates = df[DATE_COLUMN].isna().sum()

duplicate_dates = df[DATE_COLUMN].duplicated().sum()

missing_values = filtered_df.isna().sum().sum()

quality_col1.metric(
    "Missing Dates",
    int(missing_dates)
)

quality_col2.metric(
    "Duplicate Dates",
    int(duplicate_dates)
)

quality_col3.metric(
    "Missing Values",
    int(missing_values)
)

# -------------------------------------------------
# LOGICAL VALIDATION
# -------------------------------------------------

st.subheader("Logical Constraint Validation")

transfer_error = (
    filtered_df[TRANSFER_COLUMN]
    > filtered_df[CBP_COLUMN]
).sum()

discharge_error = (
    filtered_df[DISCHARGE_COLUMN]
    > filtered_df[HHS_COLUMN]
).sum()

v1, v2 = st.columns(2)

v1.metric(
    "Transfers > CBP Custody",
    int(transfer_error)
)

v2.metric(
    "Discharges > HHS Care",
    int(discharge_error)
)

# -------------------------------------------------
# RAW DATA
# -------------------------------------------------

st.header("📋 Data Preview")

st.dataframe(
    filtered_df,
    use_container_width=True
)

# -------------------------------------------------
# DOWNLOAD
# -------------------------------------------------

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="📥 Download Processed Data",
    data=csv,
    file_name="processed_hhs_data.csv",
    mime="text/csv"
)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.markdown("---")

st.caption(
    "HHS Data Analysis & Forecasting Application"
)