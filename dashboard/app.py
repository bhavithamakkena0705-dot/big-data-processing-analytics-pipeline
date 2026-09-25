
import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import os

st.set_page_config(
    page_title="Big Data Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Big Data Processing & Analytics Pipeline")
st.subheader("Sales Analytics Dashboard")

# -----------------------------
# Load Processed Data
# -----------------------------
city_files = glob.glob(
    "big_data_pipeline/data/processed/city_sales/*.csv"
)

product_files = glob.glob(
    "big_data_pipeline/data/processed/product_sales/*.csv"
)

if not city_files or not product_files:
    st.error("Processed data files are not available.")
    st.stop()

city_df = pd.read_csv(city_files[0])
product_df = pd.read_csv(product_files[0])

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔎 Filters")

cities = ["All Cities"] + sorted(city_df["City"].unique().tolist())
selected_city = st.sidebar.radio("Select City", cities)

products = ["All Products"] + sorted(product_df["Product"].unique().tolist())
selected_product = st.sidebar.radio("Select Product", products)

# -----------------------------
# Apply Filters
# -----------------------------
filtered_city = city_df.copy()
filtered_product = product_df.copy()

if selected_city != "All Cities":
    filtered_city = filtered_city[
        filtered_city["City"] == selected_city
    ]

if selected_product != "All Products":
    filtered_product = filtered_product[
        filtered_product["Product"] == selected_product
    ]

# -----------------------------
# KPI Metrics
# -----------------------------
total_sales = filtered_city["Total_Sales"].sum()
total_cities = len(filtered_city)
total_products = len(filtered_product)

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Sales", f"₹{total_sales:,.0f}")
col2.metric("🏙️ Cities", total_cities)
col3.metric("📦 Products", total_products)

st.divider()

# -----------------------------
# City-wise Sales
# -----------------------------
st.subheader("🏙️ City-wise Sales")

col1, col2 = st.columns(2)

with col1:
    fig_city = px.bar(
        filtered_city,
        x="City",
        y="Total_Sales",
        title="Sales by City",
        text="Total_Sales"
    )
    st.plotly_chart(fig_city, use_container_width=True)

with col2:
    st.dataframe(
        filtered_city,
        use_container_width=True,
        hide_index=True
    )

st.download_button(
    "⬇️ Download City Sales Report",
    filtered_city.to_csv(index=False),
    "city_sales_report.csv",
    "text/csv"
)

st.divider()

# -----------------------------
# Product-wise Sales
# -----------------------------
st.subheader("📦 Product-wise Sales")

col1, col2 = st.columns(2)

with col1:
    fig_product = px.bar(
        filtered_product,
        x="Product",
        y="Total_Sales",
        title="Sales by Product",
        text="Total_Sales"
    )
    st.plotly_chart(fig_product, use_container_width=True)

with col2:
    st.dataframe(
        filtered_product,
        use_container_width=True,
        hide_index=True
    )

st.download_button(
    "⬇️ Download Product Sales Report",
    filtered_product.to_csv(index=False),
    "product_sales_report.csv",
    "text/csv"
)

st.divider()

# -----------------------------
# Sales Trend
# -----------------------------
st.subheader("📈 Sales Trend")

ingestion_file = "big_data_pipeline/data/ingestion/sales_data.csv"

if os.path.exists(ingestion_file):
    sales_df = pd.read_csv(ingestion_file)

    sales_df["Date"] = pd.to_datetime(sales_df["Date"])

    if selected_city != "All Cities":
        sales_df = sales_df[
            sales_df["City"] == selected_city
        ]

    if selected_product != "All Products":
        sales_df = sales_df[
            sales_df["Product"] == selected_product
        ]

    fig_trend = px.line(
        sales_df,
        x="Date",
        y="Sales",
        markers=True,
        title="Daily Sales Trend"
    )

    st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------------
# Product Distribution
# -----------------------------
st.subheader("🥧 Product Sales Distribution")

fig_pie = px.pie(
    filtered_product,
    names="Product",
    values="Total_Sales",
    title="Product Sales Distribution"
)

st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------
# Footer
# -----------------------------
st.divider()

st.caption(
    "Big Data Processing & Analytics Pipeline | "
    "PySpark + Python + Streamlit + Plotly"
)
