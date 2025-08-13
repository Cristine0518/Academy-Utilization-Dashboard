import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Academy Dashboard", layout="wide")

# Title and description
st.title('🎈 Academy Dashboard App')
st.write('Welcome to the Academy Dashboard!')

# Load data from Excel file
@st.cache_data
def load_data():
    xls = pd.ExcelFile("Volante_UtilizationLog_12AUG2025.txt.xlsm", engine="openpyxl")
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[1])
    df.columns = df.columns.str.strip()
    df["TimeStamp"] = pd.to_datetime(df["TimeStamp"], errors='coerce')
    df["Date"] = df["TimeStamp"].dt.normalize()  # Convert to Timestamp with time 00:00:00
    return df.dropna(subset=["Date", "Activity Category", "Working Hrs Spent"])

# Load and validate data
try:
    df = load_data()
    required_columns = ["Activity Category", "Date", "Working Hrs Spent", "Specific Outcome/s"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Missing columns in dataset: {missing}")
        st.stop()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
categories = st.sidebar.multiselect(
    "Select Activity Categories",
    options=df["Activity Category"].dropna().unique(),
    default=df["Activity Category"].dropna().unique()
)
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["Date"].min().date(), df["Date"].max().date()]
)

# Filter data
start_date = pd.Timestamp(date_range[0])
end_date = pd.Timestamp(date_range[1])
filtered_df = df[
    (df["Activity Category"].isin(categories)) &
    (df["Date"] >= start_date) &
    (df["Date"] <= end_date)
]

# Layout with columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Activity Log")
    st.dataframe(filtered_df)

with col2:
    st.subheader("Total Hours by Activity Category")
    category_hours = filtered_df.groupby("Activity Category")["Working Hrs Spent"].sum().reset_index()
    fig_bar = px.bar(
        category_hours,
        x="Working Hrs Spent",
        y="Activity Category",
        orientation="h",
        title="Total Hours per Activity Category",
        labels={"Working Hrs Spent": "Hours", "Activity Category": "Category"},
        text="Working Hrs Spent"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# Daily Activity Breakdown - Bar Chart
st.subheader("Daily Activity Breakdown")
daily_hours_bar = filtered_df.groupby("Date")["Working Hrs Spent"].sum().reset_index()
fig_daily_bar = px.bar(
    daily_hours_bar,
    x="Date",
    y="Working Hrs Spent",
    title="Daily Activity Breakdown",
    labels={"Working Hrs Spent": "Hours"}
)
st.plotly_chart(fig_daily_bar, use_container_width=True)

# Daily Working Hours Distribution - Line Chart
st.subheader("Daily Working Hours Distribution")
fig_line = px.line(
    daily_hours_bar,
    x="Date",
    y="Working Hrs Spent",
    title="Daily Working Hours Distribution",
    labels={"Working Hrs Spent": "Hours"}
)
st.plotly_chart(fig_line, use_container_width=True)

# Pie Chart of Total Hours Worked for the Week
st.subheader("Weekly Utilization Pie Chart")
total_hours = daily_hours_bar["Working Hrs Spent"].sum()
max_hours = 37.5
utilized = min(total_hours, max_hours)
remaining = max(0, max_hours - utilized)
pie_data = pd.DataFrame({
    "Category": ["Utilized Hours", "Remaining Capacity"],
    "Hours": [utilized, remaining]
})
fig_pie = px.pie(
    pie_data,
    names="Category",
    values="Hours",
    title=f"Total Hours Worked for the Week (Max: {max_hours} hrs)",
    hole=0.4
)
st.plotly_chart(fig_pie, use_container_width=True)

# Top 5 Most Time-Consuming Activities
st.subheader("Top 5 Most Time-Consuming Activities")
top_activities = (
    filtered_df.sort_values("Working Hrs Spent", ascending=False)
    .head(5)[["TimeStamp", "Activity Category", "Specific Outcome/s", "Working Hrs Spent"]]
)
st.table(top_activities)
