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

    c1, c2, c3 = st.columns(3)

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
        if st.button("Open Healthcare Dashboard", key="home_health", use_container_width=True):
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
        if st.button("Open Retail Dashboard", key="home_retail", use_container_width=True):
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
        if st.button("Open Education Dashboard", key="home_education", use_container_width=True):
            open_domain("education")
            st.rerun()

    st.markdown("---")
    st.info(
        "Pipeline capabilities: Apache Spark processing • Multi-domain analytics • "
        "Automatic anomaly detection • Key-record identification • Intelligent insights • "
        "Real-time updates • CSV dataset analysis"
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
else:
    go_home()
    st.rerun()
