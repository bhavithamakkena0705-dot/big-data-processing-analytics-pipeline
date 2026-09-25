import streamlit as st
import pandas as pd
import plotly.express as px
import glob

st.set_page_config(
    page_title="Big Data Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

if not st.session_state.get("authenticated", False):

    st.title("🔐 Secure Login")
    st.write("Please login to access the Big Data Analytics Dashboard.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if "username" not in st.secrets or "password" not in st.secrets:
            st.error("Login settings are not configured.")
        elif (
            username == st.secrets["username"]
            and password == st.secrets["password"]
        ):
            st.session_state["authenticated"] = True
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

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

st.markdown("---")
st.header("🤖 Machine Learning - Sales Prediction")

ml_files = glob.glob("data/ingestion/sales_data.csv")

if ml_files:

    ml_df = pd.read_csv(ml_files[0])

    ml_df["Date"] = pd.to_datetime(ml_df["Date"])

    # Convert Date into numerical Day value
    ml_df["Day"] = (
        ml_df["Date"] - ml_df["Date"].min()
    ).dt.days

    # Features and target
    X = ml_df[["Day", "Quantity"]]
    y = ml_df["Sales"]

    # Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predictions
    ml_df["Predicted_Sales"] = model.predict(X)

    # Model evaluation
    mae = mean_absolute_error(
        ml_df["Sales"],
        ml_df["Predicted_Sales"]
    )

    r2 = r2_score(
        ml_df["Sales"],
        ml_df["Predicted_Sales"]
    )

    # Metrics
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Mean Absolute Error",
            f"₹{mae:,.2f}"
        )

    with col2:
        st.metric(
            "R² Score",
            f"{r2:.2f}"
        )

    # Actual vs Predicted chart
    fig_ml = px.line(
        ml_df,
        x="Date",
        y=["Sales", "Predicted_Sales"],
        markers=True,
        title="Actual Sales vs Predicted Sales"
    )

    fig_ml.update_layout(
        xaxis_title="Date",
        yaxis_title="Sales",
        legend_title="Values"
    )

    st.plotly_chart(
        fig_ml,
        use_container_width=True
    )

    # Prediction table
    st.subheader("📋 Sales Prediction Results")

    st.dataframe(
        ml_df[
            [
                "Date",
                "Sales",
                "Quantity",
                "Predicted_Sales"
            ]
        ],
        use_container_width=True
    )

else:

    st.warning(
        "Sales dataset for Machine Learning is not available."
    )
