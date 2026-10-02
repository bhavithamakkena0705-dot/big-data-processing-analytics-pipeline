import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import os
import glob
from datetime import datetime

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Multi-Domain Big Data Analytics System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# SESSION STATE / NAVIGATION
# ============================================================
if "selected_domain" not in st.session_state:
    st.session_state.selected_domain = None

def go_home():
    st.session_state.selected_domain = None

def open_domain(domain):
    st.session_state.selected_domain = domain

# ============================================================
# COMMON UI
# ============================================================
st.markdown("""
<style>
.domain-card {
    padding: 24px;
    border: 1px solid rgba(128,128,128,.25);
    border-radius: 18px;
    min-height: 245px;
    background: rgba(128,128,128,.06);
    margin-bottom: 10px;
}
.domain-icon {
    font-size: 48px;
}
.domain-title {
    font-size: 25px;
    font-weight: 700;
    margin-top: 8px;
}
.domain-text {
    min-height: 65px;
    color: #777;
}
.dashboard-header {
    padding: 8px 0 18px 0;
}
</style>
""", unsafe_allow_html=True)

def page_header(title, subtitle):
    st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
    st.title(title)
    st.subheader(subtitle)
    st.markdown('</div>', unsafe_allow_html=True)

def back_button():
    if st.button("← Back to Domain Selection", use_container_width=False):
        go_home()
        st.rerun()

# ============================================================
# DOMAIN SELECTION HOME PAGE
# ============================================================
def show_home():
    st.title("📊 Multi-Domain Big Data Analytics System")
    st.subheader("Big Data Processing, Real-Time Analytics & Intelligent Insights")
    st.write(
        "Select a domain to open its dedicated analytics dashboard. "
        "Each domain is processed and displayed independently."
    )

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="domain-card">
            <div class="domain-icon">🏥</div>
            <div class="domain-title">Healthcare Domain</div>
            <div class="domain-text">
                Patient analytics, treatment-cost analysis, length-of-stay
                analysis, risk detection and hospital information search.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Open Healthcare Dashboard",
            key="home_health",
            use_container_width=True
        ):
            open_domain("healthcare")
            st.rerun()

    with c2:
        st.markdown("""
        <div class="domain-card">
            <div class="domain-icon">🛒</div>
            <div class="domain-title">Retail Domain</div>
            <div class="domain-text">
                Sales, quantity, city-wise and product-wise analytics,
                top-performing records, trends and anomaly detection.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Open Retail Dashboard",
            key="home_retail",
            use_container_width=True
        ):
            open_domain("retail")
            st.rerun()

    with c3:
        st.markdown("""
        <div class="domain-card">
            <div class="domain-icon">🎓</div>
            <div class="domain-title">Education Domain</div>
            <div class="domain-text">
                Student performance, marks, attendance, anomaly detection,
                key-record detection and real-time streaming analytics.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Open Education Dashboard",
            key="home_education",
            use_container_width=True
        ):
            open_domain("education")
            st.rerun()

    with c4:
        st.markdown("""
        <div class="domain-card">
            <div class="domain-icon">🏦</div>
            <div class="domain-title">Banking Domain</div>
            <div class="domain-text">
                Transaction analytics, deposits and withdrawals,
                customer activity, loan analysis, anomaly detection
                and nearby bank identification.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Open Banking Dashboard",
            key="home_banking",
            use_container_width=True
        ):
            open_domain("banking")
            st.rerun()

    st.markdown("---")
    st.info(
        "Pipeline capabilities: Apache Spark processing • Multi-domain analytics • "
        "Automatic anomaly detection • Key-record identification • Intelligent insights • "
        "Real-time updates • CSV dataset analysis • Location-based banking search"
    )

# ============================================================
# HEALTHCARE DASHBOARD
# ============================================================
def show_healthcare():
    page_header(
        "🏥 Healthcare Analytics Dashboard",
        "Patient, treatment, risk and hospital information analytics"
    )
    back_button()
    st.markdown("---")

    healthcare_file = "/content/big_data_project/data/domains/healthcare/healthcare_data.csv"

    try:
        healthcare_df = pd.read_csv(healthcare_file)

        healthcare_df["Risk_Status"] = "NORMAL"
        healthcare_df.loc[
            (healthcare_df["Visits"] >= 7) &
            (healthcare_df["Treatment_Cost"] >= 50000) &
            (healthcare_df["Length_of_Stay"] >= 8),
            "Risk_Status"
        ] = "HIGH RISK"

        healthcare_df.loc[
            (
                (healthcare_df["Visits"] >= 7) |
                (healthcare_df["Treatment_Cost"] >= 50000) |
                (healthcare_df["Length_of_Stay"] >= 8)
            ) &
            (healthcare_df["Risk_Status"] != "HIGH RISK"),
            "Risk_Status"
        ] = "ATTENTION REQUIRED"

        total_patients = len(healthcare_df)
        total_cost = healthcare_df["Treatment_Cost"].sum()
        average_age = healthcare_df["Age"].mean()
        average_visits = healthcare_df["Visits"].mean()
        average_stay = healthcare_df["Length_of_Stay"].mean()
        high_risk = (healthcare_df["Risk_Status"] == "HIGH RISK").sum()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Patients", total_patients)
        c2.metric("Average Age", f"{average_age:.1f}")
        c3.metric("Average Visits", f"{average_visits:.2f}")
        c4.metric("Total Treatment Cost", f"₹{total_cost:,.0f}")
        c5.metric("High-Risk Patients", high_risk)

        st.markdown("---")

        left, right = st.columns(2)

        with left:
            st.subheader("🏥 Department-wise Statistics")
            department_stats = healthcare_df.groupby("Department").agg(
                Patients=("Patient_ID", "count"),
                Average_Age=("Age", "mean"),
                Average_Visits=("Visits", "mean"),
                Total_Treatment_Cost=("Treatment_Cost", "sum"),
                Average_Length_of_Stay=("Length_of_Stay", "mean")
            ).reset_index().round(2)
            st.dataframe(department_stats, use_container_width=True, hide_index=True)

        with right:
            st.subheader("💰 Treatment Cost by Department")
            cost_by_department = healthcare_df.groupby("Department")["Treatment_Cost"].sum()
            st.bar_chart(cost_by_department)

        st.subheader("🛏️ Length of Stay Analysis")
        stay_by_department = healthcare_df.groupby("Department")["Length_of_Stay"].mean()
        st.bar_chart(stay_by_department)
        st.caption(f"Overall average length of stay: {average_stay:.2f} days")

        st.subheader("⚠️ Automatic Anomaly & High-Risk Detection")
        risk_data = healthcare_df[healthcare_df["Risk_Status"] != "NORMAL"]
        if not risk_data.empty:
            st.dataframe(
                risk_data[
                    ["Patient_ID", "Department", "Age", "Visits",
                     "Treatment_Cost", "Length_of_Stay", "Risk_Status"]
                ],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("No high-risk or attention-required records detected.")

        st.subheader("🔑 Key Patient Record")
        key_patient = healthcare_df.loc[healthcare_df["Treatment_Cost"].idxmax()]
        st.info(
            f"Highest treatment-cost record: Patient {key_patient['Patient_ID']} | "
            f"{key_patient['Department']} | Treatment Cost ₹{key_patient['Treatment_Cost']:,.0f} | "
            f"Visits {key_patient['Visits']} | Stay {key_patient['Length_of_Stay']} days"
        )

        st.subheader("💡 Automatic Healthcare Insights")
        if high_risk > 0:
            st.warning(f"{high_risk} high-risk patient record(s) detected automatically.")
        if healthcare_df["Treatment_Cost"].max() >= 50000:
            st.info("High treatment-cost cases require additional attention.")
        if average_stay < 5:
            st.info("Average hospital stay is relatively short.")

        # Hospital web search
        st.markdown("---")
        st.header("🌐 Hospital Information Search")
        st.write(
            "Search a hospital name to retrieve publicly available location "
            "and geographic information from OpenStreetMap."
        )

        hospital_name = st.text_input(
            "Enter Hospital Name",
            placeholder="Example: RIMS General Hospital",
            key="health_hospital_name"
        )

        if st.button("🔎 Search Hospital Details", key="health_hospital_search"):
            if hospital_name.strip():
                try:
                    import requests

                    response = requests.get(
                        "https://nominatim.openstreetmap.org/search",
                        params={
                            "q": hospital_name.strip(),
                            "format": "json",
                            "addressdetails": 1,
                            "limit": 5
                        },
                        headers={"User-Agent": "BigDataAnalyticsDashboard/1.0"},
                        timeout=15
                    )
                    results = response.json()

                    if results:
                        selected = results[0]
                        display_name = selected.get("display_name", hospital_name)
                        latitude = selected.get("lat", "Not available")
                        longitude = selected.get("lon", "Not available")
                        address = selected.get("address", {})

                        st.success(f"{len(results)} web result(s) found.")
                        st.subheader("🏥 Hospital Details")
                        a, b = st.columns(2)
                        a.metric("Hospital Name", hospital_name)
                        a.write("**📍 Location:**", display_name)
                        b.write("**🌐 Data Source:** OpenStreetMap")
                        b.write("**🏷️ Place Type:**", selected.get("type", "Not available"))

                        address_data = {
                            "House / Building": address.get("house_number", "Not available"),
                            "Road": address.get("road", "Not available"),
                            "Area": address.get("suburb", address.get("neighbourhood", "Not available")),
                            "City": address.get("city", address.get("town", address.get("village", "Not available"))),
                            "District": address.get("county", "Not available"),
                            "State": address.get("state", "Not available"),
                            "Country": address.get("country", "Not available"),
                            "Postal Code": address.get("postcode", "Not available")
                        }
                        st.subheader("📍 Address Information")
                        st.dataframe(
                            pd.DataFrame(list(address_data.items()), columns=["Field", "Value"]),
                            use_container_width=True,
                            hide_index=True
                        )

                        g1, g2 = st.columns(2)
                        g1.metric("Latitude", latitude)
                        g2.metric("Longitude", longitude)

                        try:
                            st.map(pd.DataFrame({
                                "latitude": [float(latitude)],
                                "longitude": [float(longitude)]
                            }))
                        except Exception:
                            pass

                        if len(results) > 1:
                            st.subheader("🔎 Other Matching Hospital Results")
                            st.dataframe(
                                pd.DataFrame([
                                    {
                                        "Name": item.get("display_name", "Not available"),
                                        "Type": item.get("type", "Not available"),
                                        "Latitude": item.get("lat", "Not available"),
                                        "Longitude": item.get("lon", "Not available")
                                    }
                                    for item in results
                                ]),
                                use_container_width=True,
                                hide_index=True
                            )
                    else:
                        st.warning("No matching hospital data found on the web.")
                except Exception as e:
                    st.error(f"Hospital web data error: {e}")
            else:
                st.warning("Please enter a hospital name.")

    except Exception as e:
        st.error(f"Healthcare analytics error: {e}")

# ============================================================
# RETAIL DASHBOARD
# ============================================================
def show_retail():
    page_header(
        "🛒 Retail Analytics Dashboard",
        "Sales, product, city and intelligent retail analytics"
    )
    back_button()
    st.markdown("---")

    retail_file = "/content/big_data_project/data/domains/retail/retail_sales.csv"

    try:
        retail_df = pd.read_csv(retail_file)

        total_sales = retail_df["Sales"].sum()
        total_quantity = retail_df["Quantity"].sum()
        average_sales = retail_df["Sales"].mean()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Sales", f"₹{total_sales:,.0f}")
        c2.metric("Total Quantity", f"{total_quantity:,.0f}")
        c3.metric("Average Sales", f"₹{average_sales:,.2f}")
        c4.metric("Total Records", len(retail_df))

        st.markdown("---")

        left, right = st.columns(2)
        with left:
            st.subheader("🏙️ City-wise Sales")
            city_sales = retail_df.groupby("City")["Sales"].sum().sort_values(ascending=False)
            st.bar_chart(city_sales)

        with right:
            st.subheader("📦 Product-wise Sales")
            product_sales = retail_df.groupby("Product")["Sales"].sum().sort_values(ascending=False)
            st.bar_chart(product_sales)

        top_city = city_sales.idxmax()
        top_product = product_sales.idxmax()

        st.subheader("🏆 Key Retail Records")
        k1, k2 = st.columns(2)
        k1.info(f"Top-performing city: {top_city} — ₹{city_sales.max():,.0f}")
        k2.info(f"Top-performing product: {top_product} — ₹{product_sales.max():,.0f}")

        st.subheader("📈 Sales Trend")
        trend_df = retail_df.copy()
        trend_df["Date"] = pd.to_datetime(trend_df["Date"], errors="coerce")
        trend_df = trend_df.dropna(subset=["Date"]).groupby("Date")["Sales"].sum()
        st.line_chart(trend_df)

        st.subheader("⚠️ Automatic Retail Anomaly Detection")
        sales_mean = retail_df["Sales"].mean()
        sales_std = retail_df["Sales"].std()
        threshold = sales_mean + sales_std if pd.notna(sales_std) else sales_mean
        retail_df["Anomaly"] = retail_df["Sales"].apply(
            lambda x: "High Sales Record" if x > threshold else "Normal"
        )
        anomalies = retail_df[retail_df["Anomaly"] != "Normal"]

        if not anomalies.empty:
            st.dataframe(
                anomalies[["Date", "City", "Product", "Sales", "Quantity", "Anomaly"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("No retail sales anomalies detected.")

        st.subheader("💡 Automatic Retail Insights")
        key_record = retail_df.loc[retail_df["Sales"].idxmax()]
        st.info(
            f"Highest sales record: {key_record['Product']} in {key_record['City']} "
            f"with sales of ₹{key_record['Sales']:,.0f}."
        )

        # Preserve CSV upload capability in the retail domain.
        st.markdown("---")
        st.header("📂 CSV Upload & Automatic Dataset Analysis")
        st.write(
            "Upload any CSV dataset and automatically inspect its structure, "
            "quality and numeric columns."
        )

        uploaded_file = st.file_uploader(
            "Upload CSV Dataset",
            type=["csv"],
            key="retail_automatic_csv_upload"
        )

        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                total_rows = uploaded_df.shape[0]
                total_columns = uploaded_df.shape[1]
                missing_values = int(uploaded_df.isnull().sum().sum())
                duplicate_rows = int(uploaded_df.duplicated().sum())

                st.success(f"Dataset '{uploaded_file.name}' loaded successfully!")

                a, b, c, d = st.columns(4)
                a.metric("Total Records", total_rows)
                b.metric("Total Columns", total_columns)
                c.metric("Missing Values", missing_values)
                d.metric("Duplicate Rows", duplicate_rows)

                st.subheader("📋 Automatic Column Detection")
                column_info = pd.DataFrame({
                    "Column Name": uploaded_df.columns,
                    "Data Type": [str(dtype) for dtype in uploaded_df.dtypes],
                    "Missing Values": [
                        int(uploaded_df[column].isnull().sum())
                        for column in uploaded_df.columns
                    ],
                    "Unique Values": [
                        int(uploaded_df[column].nunique())
                        for column in uploaded_df.columns
                    ]
                })
                st.dataframe(column_info, use_container_width=True, hide_index=True)

                st.subheader("👀 Dataset Preview")
                st.dataframe(uploaded_df.head(10), use_container_width=True, hide_index=True)

                numeric_columns = uploaded_df.select_dtypes(include="number").columns.tolist()
                if numeric_columns:
                    st.subheader("📈 Automatic Numeric Analysis")
                    st.dataframe(
                        uploaded_df[numeric_columns].describe().T[
                            ["count", "mean", "min", "max"]
                        ].round(2),
                        use_container_width=True
                    )
                    selected_column = st.selectbox(
                        "Select Numeric Column for Analysis",
                        numeric_columns,
                        key="retail_uploaded_numeric_column"
                    )
                    st.bar_chart(uploaded_df[selected_column].value_counts().head(10))
                    st.info(
                        f"Average {selected_column}: "
                        f"{uploaded_df[selected_column].mean():.2f}"
                    )
                    st.success(
                        f"Highest {selected_column}: "
                        f"{uploaded_df[selected_column].max()}"
                    )
                    st.warning(
                        f"Lowest {selected_column}: "
                        f"{uploaded_df[selected_column].min()}"
                    )

                st.subheader("🔍 Automatic Data Quality Check")
                if missing_values == 0:
                    st.success("No missing values detected.")
                else:
                    st.warning(f"{missing_values} missing value(s) detected.")
                if duplicate_rows == 0:
                    st.success("No duplicate records detected.")
                else:
                    st.warning(f"{duplicate_rows} duplicate record(s) detected.")
            except Exception as e:
                st.error(f"Dataset analysis error: {e}")

    except Exception as e:
        st.error(f"Retail analytics error: {e}")


# ============================================================
# BANKING DASHBOARD
# ============================================================

def show_banking():
    st.title("🏦 Banking Big Data Analytics Dashboard")
    st.subheader(
        "Transaction Analytics • Customer Intelligence • "
        "Anomaly Detection • Location-Based Bank Identification"
    )

    banking_file = (
        "/content/big_data_project/"
        "data/domains/banking/banking_data.csv"
    )

    try:
        banking_df = pd.read_csv(banking_file)
    except Exception as e:
        st.error(f"Unable to load banking dataset: {e}")
        return

    banking_df["Date"] = pd.to_datetime(
        banking_df["Date"], errors="coerce"
    )

    banking_df["Transaction_Amount"] = pd.to_numeric(
        banking_df["Transaction_Amount"], errors="coerce"
    ).fillna(0)

    banking_df["Loan_Amount"] = pd.to_numeric(
        banking_df["Loan_Amount"], errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    st.markdown("### 🔎 Banking Filters")

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        account_types = ["All"] + sorted(
            banking_df["Account_Type"].dropna().unique().tolist()
        )
        selected_account = st.selectbox(
            "Account Type",
            account_types,
            key="bank_account_filter"
        )

    with f2:
        transaction_types = ["All"] + sorted(
            banking_df["Transaction_Type"].dropna().unique().tolist()
        )
        selected_transaction = st.selectbox(
            "Transaction Type",
            transaction_types,
            key="bank_transaction_filter"
        )

    with f3:
        cities = ["All"] + sorted(
            banking_df["City"].dropna().unique().tolist()
        )
        selected_city = st.selectbox(
            "City / Branch",
            cities,
            key="bank_city_filter"
        )

    with f4:
        categories = ["All"] + sorted(
            banking_df["Customer_Category"].dropna().unique().tolist()
        )
        selected_category = st.selectbox(
            "Customer Category",
            categories,
            key="bank_category_filter"
        )

    filtered_df = banking_df.copy()

    if selected_account != "All":
        filtered_df = filtered_df[
            filtered_df["Account_Type"] == selected_account
        ]

    if selected_transaction != "All":
        filtered_df = filtered_df[
            filtered_df["Transaction_Type"] == selected_transaction
        ]

    if selected_city != "All":
        filtered_df = filtered_df[
            filtered_df["City"] == selected_city
        ]

    if selected_category != "All":
        filtered_df = filtered_df[
            filtered_df["Customer_Category"] == selected_category
        ]

    # --------------------------------------------------------
    # DATE FILTER
    # --------------------------------------------------------

    if not filtered_df.empty:
        min_date = filtered_df["Date"].min().date()
        max_date = filtered_df["Date"].max().date()

        date_range = st.date_input(
            "Transaction Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="bank_date_filter"
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range

            filtered_df = filtered_df[
                (filtered_df["Date"].dt.date >= start_date)
                & (filtered_df["Date"].dt.date <= end_date)
            ]

    st.markdown("---")

    # --------------------------------------------------------
    # KEY METRICS
    # --------------------------------------------------------

    total_customers = filtered_df["Customer_ID"].nunique()
    total_accounts = len(filtered_df)
    total_transactions = len(filtered_df)
    total_amount = filtered_df["Transaction_Amount"].sum()

    avg_transaction = (
        filtered_df["Transaction_Amount"].mean()
        if not filtered_df.empty else 0
    )

    deposits = filtered_df.loc[
        filtered_df["Transaction_Type"] == "Deposit",
        "Transaction_Amount"
    ].sum()

    withdrawals = filtered_df.loc[
        filtered_df["Transaction_Type"] == "Withdrawal",
        "Transaction_Amount"
    ].sum()

    total_loans = filtered_df["Loan_Amount"].sum()

    active_accounts = (
        filtered_df["Account_Status"] == "Active"
    ).sum()

    inactive_accounts = (
        filtered_df["Account_Status"] == "Inactive"
    ).sum()

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("👥 Total Customers", total_customers)
    m2.metric("🏦 Total Accounts", total_accounts)
    m3.metric("💳 Transactions", total_transactions)
    m4.metric("💰 Transaction Amount", f"₹{total_amount:,.0f}")

    m5, m6, m7, m8 = st.columns(4)

    m5.metric("📊 Avg Transaction", f"₹{avg_transaction:,.0f}")
    m6.metric("📥 Deposits", f"₹{deposits:,.0f}")
    m7.metric("📤 Withdrawals", f"₹{withdrawals:,.0f}")
    m8.metric("💵 Loan Amount", f"₹{total_loans:,.0f}")

    m9, m10 = st.columns(2)

    m9.metric("🟢 Active Accounts", active_accounts)
    m10.metric("🔴 Inactive Accounts", inactive_accounts)

    st.markdown("---")

    # --------------------------------------------------------
    # CHARTS
    # --------------------------------------------------------

    st.markdown("### 📈 Banking Analytics")

    chart1, chart2 = st.columns(2)

    with chart1:
        daily_transactions = (
            filtered_df.groupby("Date")
            .agg(Transaction_Amount=("Transaction_Amount", "sum"))
            .reset_index()
        )

        fig = px.line(
            daily_transactions,
            x="Date",
            y="Transaction_Amount",
            markers=True,
            title="Transactions by Date"
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Transaction Amount"
        )
        st.plotly_chart(fig, use_container_width=True)

    with chart2:
        transaction_summary = (
            filtered_df.groupby("Transaction_Type")
            ["Transaction_Amount"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            transaction_summary,
            x="Transaction_Type",
            y="Transaction_Amount",
            title="Deposits vs Withdrawals",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    chart3, chart4 = st.columns(2)

    with chart3:
        account_summary = (
            filtered_df.groupby("Account_Type")
            ["Transaction_Amount"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            account_summary,
            x="Account_Type",
            y="Transaction_Amount",
            title="Transactions by Account Type",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with chart4:
        city_summary = (
            filtered_df.groupby("City")
            ["Transaction_Amount"]
            .sum()
            .reset_index()
            .sort_values("Transaction_Amount", ascending=False)
        )

        fig = px.bar(
            city_summary,
            x="City",
            y="Transaction_Amount",
            title="Transactions by City",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    chart5, chart6 = st.columns(2)

    with chart5:
        loan_summary = (
            filtered_df.groupby("City")
            ["Loan_Amount"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            loan_summary,
            names="City",
            values="Loan_Amount",
            title="Loan Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    with chart6:
        branch_summary = (
            filtered_df.groupby("Branch")
            ["Transaction_Amount"]
            .sum()
            .reset_index()
            .sort_values("Transaction_Amount", ascending=False)
        )

        fig = px.bar(
            branch_summary,
            x="Branch",
            y="Transaction_Amount",
            title="Branch-wise Transaction Volume",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # CUSTOMER ACTIVITY
    # --------------------------------------------------------

    st.markdown("### 👤 Customer Activity")

    if not filtered_df.empty:
        customer_activity = (
            filtered_df.groupby(
                ["Customer_ID", "Customer_Name"]
            )
            .agg(
                Transactions=("Transaction_ID", "count"),
                Total_Amount=("Transaction_Amount", "sum")
            )
            .reset_index()
            .sort_values(
                ["Transactions", "Total_Amount"],
                ascending=False
            )
        )

        st.dataframe(
            customer_activity,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # ANOMALY DETECTION
    # --------------------------------------------------------

    st.markdown("### 🚨 Transaction Anomaly Detection")

    anomaly_df = filtered_df.copy()

    if not anomaly_df.empty:

        amount_mean = anomaly_df["Transaction_Amount"].mean()
        amount_std = anomaly_df["Transaction_Amount"].std()

        if pd.isna(amount_std):
            amount_std = 0

        high_threshold = amount_mean + amount_std

        def classify_transaction(row):
            amount = row["Transaction_Amount"]

            if amount >= max(high_threshold, 100000):
                return "HIGH RISK"

            if amount >= max(amount_mean + (amount_std * 0.5), 75000):
                return "WARNING"

            return "NORMAL"

        anomaly_df["Risk_Status"] = anomaly_df.apply(
            classify_transaction,
            axis=1
        )

        risk_counts = (
            anomaly_df["Risk_Status"]
            .value_counts()
            .reindex(
                ["NORMAL", "WARNING", "HIGH RISK"],
                fill_value=0
            )
        )

        r1, r2, r3 = st.columns(3)

        r1.metric("🟢 NORMAL", int(risk_counts["NORMAL"]))
        r2.metric("🟡 WARNING", int(risk_counts["WARNING"]))
        r3.metric("🔴 HIGH RISK", int(risk_counts["HIGH RISK"]))

        suspicious = anomaly_df[
            anomaly_df["Risk_Status"] != "NORMAL"
        ].sort_values(
            "Transaction_Amount",
            ascending=False
        )

        if not suspicious.empty:
            st.warning(
                "Transactions requiring attention were detected."
            )
            st.dataframe(
                suspicious[
                    [
                        "Transaction_ID",
                        "Customer_Name",
                        "Transaction_Type",
                        "Transaction_Amount",
                        "City",
                        "Branch",
                        "Risk_Status"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success(
                "No warning or high-risk transactions detected."
            )

    # --------------------------------------------------------
    # AUTOMATIC INSIGHTS
    # --------------------------------------------------------

    st.markdown("### 🧠 Automatic Banking Insights")

    if not filtered_df.empty:

        highest_transaction = filtered_df.loc[
            filtered_df["Transaction_Amount"].idxmax()
        ]

        lowest_transaction = filtered_df.loc[
            filtered_df["Transaction_Amount"].idxmin()
        ]

        most_active_customer = (
            filtered_df.groupby(
                ["Customer_ID", "Customer_Name"]
            )["Transaction_ID"]
            .count()
            .sort_values(ascending=False)
            .index[0]
        )

        highest_branch = (
            filtered_df.groupby("Branch")
            ["Transaction_Amount"]
            .sum()
            .sort_values(ascending=False)
            .index[0]
        )

        i1, i2 = st.columns(2)

        with i1:
            st.info(
                f"💰 Highest Transaction: "
                f"{highest_transaction['Transaction_ID']} — "
                f"₹{highest_transaction['Transaction_Amount']:,.0f}"
            )

            st.info(
                f"📉 Lowest Transaction: "
                f"{lowest_transaction['Transaction_ID']} — "
                f"₹{lowest_transaction['Transaction_Amount']:,.0f}"
            )

        with i2:
            st.info(
                f"👤 Most Active Customer: "
                f"{most_active_customer[1]} "
                f"({most_active_customer[0]})"
            )

            st.info(
                f"🏦 Highest Transaction Branch: "
                f"{highest_branch}"
            )

        high_value = filtered_df[
            filtered_df["Transaction_Amount"] >= 100000
        ]

        if not high_value.empty:
            st.warning(
                f"⚠️ {len(high_value)} high-value transaction(s) "
                f"of ₹1,00,000 or above detected."
            )

        key_record = filtered_df.loc[
            filtered_df["Transaction_Amount"].idxmax()
        ]

        st.success(
            f"⭐ Key Record: {key_record['Transaction_ID']} | "
            f"Customer: {key_record['Customer_Name']} | "
            f"Amount: ₹{key_record['Transaction_Amount']:,.0f} | "
            f"Branch: {key_record['Branch']}"
        )

    # --------------------------------------------------------
    # CSV UPLOAD
    # --------------------------------------------------------

    st.markdown("---")
    st.markdown("### 📂 Upload Banking CSV")

    uploaded_file = st.file_uploader(
        "Upload another banking dataset",
        type=["csv"],
        key="banking_csv_upload"
    )

    if uploaded_file is not None:

        uploaded_df = pd.read_csv(uploaded_file)

        st.success(
            f"Uploaded dataset loaded successfully: "
            f"{len(uploaded_df)} rows × {len(uploaded_df.columns)} columns"
        )

        u1, u2, u3 = st.columns(3)

        u1.metric(
            "Total Rows",
            len(uploaded_df)
        )

        u2.metric(
            "Total Columns",
            len(uploaded_df.columns)
        )

        u3.metric(
            "Missing Values",
            int(uploaded_df.isnull().sum().sum())
        )

        st.dataframe(
            uploaded_df.head(20),
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # BACK TO HOME
    # --------------------------------------------------------

    st.markdown("---")

    if st.button(
        "⬅️ Back to Domain Selection",
        key="banking_back_home",
        use_container_width=True
    ):
        go_home()
        st.rerun()

# ============================================================
# EDUCATION DASHBOARD
# ============================================================
def show_education():
    page_header(
        "🎓 Education Analytics Dashboard",
        "Student performance, attendance, intelligent insights and real-time analytics"
    )
    back_button()
    st.markdown("---")

    # Real-time refresh is used only on the Education dashboard.
    st_autorefresh(interval=3000, key="education_realtime_refresh")

    input_folder = "/content/big_data_project/realtime/input"
    files = glob.glob(os.path.join(input_folder, "*.csv"))

    if not files:
        st.warning("Waiting for real-time student data...")
        return

    dataframes = []
    for file in files:
        try:
            dataframes.append(pd.read_csv(file))
        except Exception:
            pass

    if not dataframes:
        st.warning("No readable education data available.")
        return

    df = pd.concat(dataframes, ignore_index=True)

    required = {"Student_ID", "Branch", "Subject", "Marks", "Attendance"}
    if not required.issubset(df.columns):
        st.error(
            "Education stream data is missing one or more required columns: "
            + ", ".join(sorted(required))
        )
        return

    total_records = len(df)
    average_marks = df["Marks"].mean()
    average_attendance = df["Attendance"].mean()
    top_marks = df["Marks"].max()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📥 Live Student Records", total_records)
    c2.metric("📈 Average Marks", f"{average_marks:.2f}")
    c3.metric("🏆 Top Marks", top_marks)
    c4.metric("📅 Avg Attendance", f"{average_attendance:.2f}%")

    st.markdown("---")

    # Automatic anomaly detection
    df["Anomaly"] = "Normal"
    df.loc[
        (df["Marks"] < 50) & (df["Attendance"] < 70),
        "Anomaly"
    ] = "High Risk"
    df.loc[
        (df["Marks"] < 50) & (df["Attendance"] >= 70),
        "Anomaly"
    ] = "Low Marks"
    df.loc[
        (df["Marks"] >= 50) & (df["Attendance"] < 70),
        "Anomaly"
    ] = "Low Attendance"

    st.subheader("⚠️ Automatic Anomaly Detection")
    anomalies = df[df["Anomaly"] != "Normal"]
    if not anomalies.empty:
        st.dataframe(
            anomalies[
                ["Student_ID", "Branch", "Subject", "Marks", "Attendance", "Anomaly"]
            ],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No anomalies detected.")

    # Class/branch analysis
    st.subheader("🏫 Class-wise / Branch-wise Analysis")
    branch_analysis = df.groupby("Branch").agg(
        Students=("Student_ID", "count"),
        Average_Marks=("Marks", "mean"),
        Average_Attendance=("Attendance", "mean")
    ).reset_index().round(2)
    st.dataframe(branch_analysis, use_container_width=True, hide_index=True)

    # Subject analysis
    st.subheader("📚 Subject-wise Performance")
    subject_analysis = df.groupby("Subject").agg(
        Average_Marks=("Marks", "mean"),
        Average_Attendance=("Attendance", "mean"),
        Records=("Student_ID", "count")
    ).reset_index().round(2)
    st.dataframe(subject_analysis, use_container_width=True, hide_index=True)
    st.bar_chart(subject_analysis.set_index("Subject")["Average_Marks"])

    # Low-performance detection
    st.subheader("🔎 Low-Performance Student Detection")
    low_performance = df[
        (df["Marks"] < 50) | (df["Attendance"] < 70)
    ]
    if not low_performance.empty:
        st.dataframe(
            low_performance[
                ["Student_ID", "Branch", "Subject", "Marks", "Attendance", "Anomaly"]
            ],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No low-performance students detected.")

    # Key student record
    st.subheader("🔑 Key Student Record")
    top_student = df.loc[df["Marks"].idxmax()]
    st.info(
        f"Highest recorded marks: {top_student['Marks']} "
        f"({top_student['Student_ID']} - {top_student['Subject']})"
    )

    # Automatic insights
    st.subheader("💡 Automatic Insights")
    if average_marks >= 80:
        st.success("Overall performance is excellent.")
    elif average_marks >= 60:
        st.info("Overall performance is moderate.")
    else:
        st.warning("Overall performance needs improvement.")

    if average_attendance < 70:
        st.warning("Average attendance is below 70%.")
    else:
        st.success("Average attendance is satisfactory.")

    st.caption(
        f"Last dashboard update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        "| Auto-refresh: 3 seconds"
    )

# ============================================================
# ROUTER
# ============================================================
if st.session_state.selected_domain is None:
    show_home()
elif st.session_state.selected_domain == "healthcare":
    show_healthcare()
elif st.session_state.selected_domain == "retail":
    show_retail()
elif st.session_state.selected_domain == "education":
    show_education()
elif st.session_state.selected_domain == "banking":
    show_banking()
else:
    go_home()
    st.rerun()
