import streamlit as st
import pandas as pd
import plotly.express as px
import glob

st.set_page_config(
    page_title="Big Data Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.title("🔐 Secure Login")
    st.write("Please login to access the Big Data Analytics Dashboard.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if "auth" not in st.secrets:
            st.error("Authentication settings are not available.")
            st.stop()

        auth = st.secrets["auth"]

        if (
            username == auth["username"]
            and password == auth["password"]
        ):
            st.session_state.authenticated = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.stop()


st.title("📊 Big Data Processing & Analytics Pipeline")
st.subheader("India Sales Analytics Dashboard")

state_files = glob.glob("data/processed/state_sales/*.csv")
category_files = glob.glob("data/processed/category_sales/*.csv")

if not state_files or not category_files:
    st.error("Processed data files are not available.")
    st.stop()

state_df = pd.read_csv(state_files[0])
category_df = pd.read_csv(category_files[0])

if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.header("🔎 Filters")
st.sidebar.header("🎛️ Dashboard Controls")

states = ["All States"] + sorted(state_df["State"].unique().tolist())
selected_state = st.sidebar.radio("Select State", states)

filtered_state = state_df.copy()
if selected_state != "All States":
    filtered_state = filtered_state[
        filtered_state["State"] == selected_state
    ]

total_sales = filtered_state["Total_Sales"].sum()
total_states = len(filtered_state)
total_categories = len(category_df)

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Sales", f"₹{total_sales:,.2f}")
col2.metric("🇮🇳 States", total_states)
col3.metric("📦 Categories", total_categories)

st.divider()

st.subheader("📍 State-wise Sales")
col1, col2 = st.columns(2)

with col1:
    fig_state = px.bar(
        filtered_state,
        x="State",
        y="Total_Sales",
        title="Sales by State",
        text_auto=".2s"
    )
    fig_state.update_layout(
        xaxis_title="State",
        yaxis_title="Sales (₹)"
    )
    st.plotly_chart(fig_state, use_container_width=True)

with col2:
    display_state = filtered_state.copy()
    display_state["Total_Sales"] = display_state["Total_Sales"].map(
        lambda x: f"₹{x:,.2f}"
    )
    st.dataframe(display_state, use_container_width=True, hide_index=True)

st.download_button(
    "⬇️ Download State Sales Report",
    filtered_state.to_csv(index=False),
    "state_sales_report.csv",
    "text/csv"
)

st.divider()

st.subheader("📦 Category-wise Sales")
col1, col2 = st.columns(2)

with col1:
    fig_category = px.bar(
        category_df,
        x="Category",
        y="Total_Sales",
        title="Sales by Category",
        text_auto=".2s"
    )
    fig_category.update_layout(
        xaxis_title="Category",
        yaxis_title="Sales (₹)"
    )
    st.plotly_chart(fig_category, use_container_width=True)

with col2:
    display_category = category_df.copy()
    display_category["Total_Sales"] = display_category["Total_Sales"].map(
        lambda x: f"₹{x:,.2f}"
    )
    st.dataframe(display_category, use_container_width=True, hide_index=True)

st.download_button(
    "⬇️ Download Category Sales Report",
    category_df.to_csv(index=False),
    "category_sales_report.csv",
    "text/csv"
)

st.divider()

st.subheader("🥧 Category Sales Distribution")

fig_pie = px.pie(
    category_df,
    names="Category",
    values="Total_Sales",
    title="Category Sales Distribution"
)
st.plotly_chart(fig_pie, use_container_width=True)

st.divider()
st.caption(
    "Big Data Processing & Analytics Pipeline | "
    "PySpark + Python + Pandas + Streamlit + Plotly"
)
