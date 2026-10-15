import requests
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import os
import glob
from datetime import datetime
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def style_chart(fig, height=360, money_axis=False):
    """Apply a consistent, polished dark theme to Plotly charts."""
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,20,42,0.55)",
        font=dict(family="Arial, sans-serif", color="#E8F0FF", size=12),
        title=dict(font=dict(size=17, color="#F4F7FF"), x=0.02, xanchor="left"),
        margin=dict(l=18, r=18, t=62, b=24),
        hoverlabel=dict(bgcolor="#101D38", font_color="#FFFFFF", bordercolor="#35C9FF"),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(150,180,220,0.25)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(150,180,220,0.12)", zeroline=False)
    if money_axis:
        fig.update_yaxes(tickprefix="₹", separatethousands=True)
    return fig

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Big Data Processing & Analytics Pipeline",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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
# NEARBY BANK SEARCH
# ============================================================

def search_nearby_banks(location_text, bank_name="", radius=10000):
    """
    Find nearby bank branches using OpenStreetMap / Overpass.
    Returns only information available from the public map data.
    """

    try:
        headers = {
            "User-Agent": "BigDataAnalyticsPipeline/1.0"
        }

        # ----------------------------------------------------
        # 1. Convert entered location into latitude/longitude
        # ----------------------------------------------------
        geocode_url = "https://nominatim.openstreetmap.org/search"

        # Make location search more reliable
        clean_location = location_text.strip()

        if "india" not in clean_location.lower():
            clean_location = f"{clean_location}, India"

        geocode_params = {
            "q": clean_location,
            "format": "json",
            "addressdetails": 1,
            "limit": 1
        }

        geocode_response = requests.get(
            geocode_url,
            params=geocode_params,
            headers=headers,
            timeout=15
        )

        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()

        if not geocode_data:
            return None, "Location not found."

        latitude = float(geocode_data[0]["lat"])
        longitude = float(geocode_data[0]["lon"])

        # ----------------------------------------------------
        # 2. Search nearby banks using Overpass
        # ----------------------------------------------------
        overpass_url = "https://overpass-api.de/api/interpreter"

        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="bank"](around:{radius},{latitude},{longitude});
          way["amenity"="bank"](around:{radius},{latitude},{longitude});
          relation["amenity"="bank"](around:{radius},{latitude},{longitude});
        );
        out center tags;
        """

        overpass_response = requests.post(
            overpass_url,
            data=query,
            headers=headers,
            timeout=30
        )

        overpass_response.raise_for_status()
        bank_data = overpass_response.json()

        results = []

        # ----------------------------------------------------
        # 3. Extract available bank information
        # ----------------------------------------------------
        for element in bank_data.get("elements", []):

            tags = element.get("tags", {})

            name = (
                tags.get("name")
                or tags.get("brand")
                or tags.get("operator")
                or "Bank"
            )

            if bank_name:
                if bank_name.lower() not in name.lower():
                    continue

            lat = element.get("lat")
            lon = element.get("lon")

            if lat is None or lon is None:
                center = element.get("center", {})
                lat = center.get("lat")
                lon = center.get("lon")

            address_parts = [
                tags.get("addr:housenumber"),
                tags.get("addr:street"),
                tags.get("addr:suburb"),
                tags.get("addr:city"),
                tags.get("addr:state"),
                tags.get("addr:postcode")
            ]

            address = ", ".join(
                str(x) for x in address_parts if x
            )

            results.append({
                "Bank Name": name,
                "Branch": tags.get("branch", "Not available"),
                "Address": address or "Not available",
                "Phone": (
                    tags.get("phone")
                    or tags.get("contact:phone")
                    or "Not available"
                ),
                "Opening Hours": tags.get(
                    "opening_hours",
                    "Not available"
                ),
                "Services": tags.get(
                    "service",
                    "Not specified"
                ),
                "ATM": tags.get(
                    "atm",
                    "Not specified"
                ),
                "Website": tags.get(
                    "website",
                    "Not available"
                ),
                "Latitude": lat,
                "Longitude": lon
            })

        return results, {
            "latitude": latitude,
            "longitude": longitude,
            "location": geocode_data[0].get(
                "display_name",
                location_text
            )
        }

    except requests.exceptions.RequestException as e:
        return None, f"Bank search service error: {e}"

    except Exception as e:
        return None, f"Unexpected bank search error: {e}"


# ============================================================
# COMMON UI
# ============================================================
st.markdown("""
<style>
:root {
    --bg-main: #071226;
    --bg-card: rgba(13, 31, 62, .82);
    --line: rgba(77, 151, 255, .28);
    --text-main: #eef5ff;
    --text-muted: #a9bddb;
}
.stApp {
    background:
        radial-gradient(ellipse at 8% 0%, rgba(28, 94, 190, .23), transparent 35%),
        radial-gradient(ellipse at 95% 12%, rgba(120, 55, 190, .18), transparent 30%),
        linear-gradient(135deg, #050d1d 0%, #08172e 52%, #071126 100%);
    color: var(--text-main);
}
[data-testid="stHeader"] { background: rgba(4, 13, 29, .72); }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07152c 0%, #0b1e3b 100%);
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] * { color: #e7f0ff; }
.block-container { padding-top: 1.7rem; padding-bottom: 2.5rem; max-width: 1500px; }
h1, h2, h3 { color: #f4f8ff !important; letter-spacing: -.025em; }
h1 { font-weight: 800 !important; }
h2, h3 { font-weight: 700 !important; }
p, label, .stMarkdown, [data-testid="stCaptionContainer"] { color: #d0def4; }
.domain-card {
    padding: 24px 21px;
    border: 1px solid rgba(95, 157, 255, .35);
    border-radius: 20px;
    min-height: 255px;
    background: linear-gradient(145deg, rgba(19, 49, 94, .92), rgba(11, 25, 52, .94));
    box-shadow: 0 12px 30px rgba(0, 0, 0, .18), inset 0 1px 0 rgba(255,255,255,.04);
    margin-bottom: 12px;
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
.domain-card:hover {
    transform: translateY(-4px);
    border-color: rgba(75, 205, 255, .8);
    box-shadow: 0 16px 34px rgba(0, 120, 255, .15);
}
.domain-icon { font-size: 44px; filter: drop-shadow(0 0 12px rgba(63, 159, 255, .25)); }
.domain-title { font-size: 22px; font-weight: 800; margin-top: 9px; color: #f5f8ff; }
.domain-text { min-height: 78px; color: #b7c9e5; line-height: 1.55; font-size: 14px; }
.dashboard-header {
    padding: 22px 25px 20px 25px;
    margin-bottom: 16px;
    border: 1px solid rgba(70, 151, 255, .3);
    border-radius: 20px;
    background: linear-gradient(110deg, rgba(13, 43, 87, .92), rgba(19, 31, 73, .75));
    box-shadow: 0 14px 34px rgba(0, 0, 0, .16);
}
.dashboard-header h1 { margin-bottom: .25rem; }
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(19, 47, 91, .88), rgba(12, 27, 56, .92));
    border: 1px solid rgba(83, 153, 255, .32);
    padding: 17px 18px;
    border-radius: 17px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, .13);
}
[data-testid="stMetricLabel"] { color: #b8cbed !important; }
[data-testid="stMetricValue"] { color: #f4f8ff !important; font-weight: 800; }
.stButton > button {
    border: 1px solid rgba(95, 170, 255, .55);
    border-radius: 12px;
    color: #f7fbff;
    background: linear-gradient(110deg, #174aa2, #2868d8);
    font-weight: 700;
    transition: all .18s ease;
}
.stButton > button:hover {
    border-color: #72e2ff;
    color: white;
    background: linear-gradient(110deg, #2162c8, #4a54db);
    box-shadow: 0 7px 20px rgba(36, 111, 255, .24);
    transform: translateY(-1px);
}
/* Dark, readable tables across all four domains */
[data-testid="stDataFrame"], [data-testid="stTable"] {
    background: #0b1b34 !important;
    color: #eaf2ff !important;
    border: 1px solid rgba(83, 153, 255, .34) !important;
    border-radius: 13px !important;
    overflow: hidden !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, .18);
}
/* Streamlit's interactive dataframe uses a canvas; set its supported theme variables. */
[data-testid="stDataFrame"] [class*="glideDataEditor"],
[data-testid="stDataFrame"] [class*="gdg-"] {
    --gdg-bg-cell: #0b1b34;
    --gdg-bg-cell-medium: #102544;
    --gdg-bg-header: #142d50;
    --gdg-bg-header-has-focus: #1b3b67;
    --gdg-bg-header-hovered: #1b3b67;
    --gdg-text-dark: #eaf2ff;
    --gdg-text-medium: #c6d8f2;
    --gdg-text-light: #a9c0e2;
    --gdg-border-color: rgba(104, 157, 230, .24);
    --gdg-accent-color: #38bdf8;
    --gdg-link-color: #67e8f9;
}
/* Regular HTML tables, including st.table */
[data-testid="stTable"] table {
    background: #0b1b34 !important;
    color: #eaf2ff !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    width: 100% !important;
}
[data-testid="stTable"] thead tr th {
    background: #16345b !important;
    color: #f4f8ff !important;
    border-bottom: 1px solid rgba(104, 157, 230, .35) !important;
}
[data-testid="stTable"] tbody tr td {
    background: #0b1b34 !important;
    color: #dce9fb !important;
    border-bottom: 1px solid rgba(104, 157, 230, .15) !important;
}
[data-testid="stTable"] tbody tr:nth-child(even) td {
    background: #102440 !important;
}
[data-testid="stTable"] tbody tr:hover td {
    background: #17365c !important;
}
[data-testid="stAlert"] { border-radius: 13px; }
[data-baseweb="input"] > div, [data-baseweb="select"] > div,
[data-testid="stFileUploader"] section {
    background: rgba(11, 28, 56, .9);
    border-color: rgba(93, 151, 235, .35);
    border-radius: 11px;
}
hr { border-color: rgba(92, 151, 231, .22); }
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
    st.title("🚀 Big Data Processing & Analytics Pipeline")
    st.subheader("Real-Time Intelligence • Multi-Domain Analytics • Smart Insights")
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

    healthcare_file = PROJECT_ROOT / "data" / "domains" / "healthcare" / "healthcare_data.csv"

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
            cost_by_department = healthcare_df.groupby("Department", as_index=False)["Treatment_Cost"].sum().sort_values("Treatment_Cost", ascending=True)
            fig = px.bar(cost_by_department, x="Treatment_Cost", y="Department", orientation="h", text="Treatment_Cost", color="Department", color_discrete_sequence=px.colors.qualitative.Bold, title="Treatment cost comparison")
            fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside", cliponaxis=False, marker_line_width=0, opacity=0.92)
            st.plotly_chart(style_chart(fig, height=340, money_axis=True), use_container_width=True)

        st.subheader("🛏️ Length of Stay Analysis")
        stay_by_department = healthcare_df.groupby("Department", as_index=False)["Length_of_Stay"].mean().sort_values("Length_of_Stay", ascending=True)
        fig = px.bar(stay_by_department, x="Length_of_Stay", y="Department", orientation="h", text="Length_of_Stay", color="Department", color_discrete_sequence=px.colors.qualitative.Pastel, title="Average stay by department")
        fig.update_traces(texttemplate="%{text:.1f} days", textposition="outside", cliponaxis=False, marker_line_width=0)
        st.plotly_chart(style_chart(fig, height=330), use_container_width=True)
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

    retail_file = PROJECT_ROOT / "data" / "domains" / "retail" / "retail_sales.csv"

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
            city_chart_df = city_sales.rename_axis("City").reset_index(name="Sales").sort_values("Sales", ascending=True)
            fig = px.bar(city_chart_df, x="Sales", y="City", orientation="h", text="Sales", color="Sales", color_continuous_scale=["#2563EB", "#22D3EE"], title="Sales by city")
            fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside", cliponaxis=False, marker_line_width=0)
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(style_chart(fig, height=340, money_axis=True), use_container_width=True)

        with right:
            st.subheader("📦 Product-wise Sales")
            product_sales = retail_df.groupby("Product")["Sales"].sum().sort_values(ascending=False)
            product_chart_df = product_sales.rename_axis("Product").reset_index(name="Sales").sort_values("Sales", ascending=True)
            fig = px.bar(product_chart_df, x="Sales", y="Product", orientation="h", text="Sales", color="Product", color_discrete_sequence=px.colors.qualitative.Vivid, title="Sales by product")
            fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside", cliponaxis=False, marker_line_width=0)
            st.plotly_chart(style_chart(fig, height=340, money_axis=True), use_container_width=True)

        top_city = city_sales.idxmax()
        top_product = product_sales.idxmax()

        st.subheader("🏆 Key Retail Records")
        k1, k2 = st.columns(2)
        k1.info(f"Top-performing city: {top_city} — ₹{city_sales.max():,.0f}")
        k2.info(f"Top-performing product: {top_product} — ₹{product_sales.max():,.0f}")

        st.subheader("📈 Sales Trend")
        trend_df = retail_df.copy()
        trend_df["Date"] = pd.to_datetime(trend_df["Date"], errors="coerce")
        trend_df = trend_df.dropna(subset=["Date"]).groupby("Date", as_index=False)["Sales"].sum().sort_values("Date")
        if not trend_df.empty:
            fig = px.area(trend_df, x="Date", y="Sales", markers=True, title="Sales over time")
            fig.update_traces(line=dict(color="#22D3EE", width=3), fillcolor="rgba(34,211,238,0.16)", marker=dict(size=8, color="#A5F3FC"), hovertemplate="%{x|%d %b %Y}<br>Sales: ₹%{y:,.0f}<extra></extra>")
            st.plotly_chart(style_chart(fig, height=360, money_axis=True), use_container_width=True)
        else:
            st.info("No valid dates available to display a sales trend.")

        st.subheader("⚠️ Automatic Retail Anomaly Detection")
        sales_mean = retail_df["Sales"].mean()
        sales_std = retail_df["Sales"].std()
        threshold = sales_mean + sales_std if pd.notna(sales_std) else sales_mean
        retail_df["Anomaly"] = retail_df["Sales"].apply(
            lambda x: "High Sales Record" if x > threshold else "Normal"
        )
        anomalies = retail_df[retail_df["Anomaly"] != "Normal"]

        if not anomalies.empty:
            # Build a styled copy so this table follows the dashboard's dark theme.
            anomaly_table = anomalies[
                ["Date", "City", "Product", "Sales", "Quantity", "Anomaly"]
            ].copy()
            anomaly_table["Sales"] = anomaly_table["Sales"].map(
                lambda value: f"₹{value:,.0f}"
            )

            styled_anomaly_table = anomaly_table.style.set_properties(
                **{
                    "background-color": "#0B1B34",
                    "color": "#EAF2FF",
                    "border-color": "#294568",
                    "text-align": "left",
                }
            ).set_table_styles([
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#16345B"),
                        ("color", "#FFFFFF"),
                        ("font-weight", "bold"),
                        ("border-color", "#294568"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("background-color", "#0B1B34"),
                        ("color", "#EAF2FF"),
                        ("border-color", "#294568"),
                    ],
                },
                {
                    "selector": "tbody tr:nth-child(even) td",
                    "props": [("background-color", "#102440")],
                },
            ])

            # Render as a real HTML table instead of Streamlit's canvas-based
            # dataframe, which can ignore cell background styling in some versions.
            styled_anomaly_table = styled_anomaly_table.set_table_styles([
                {
                    "selector": "table",
                    "props": [
                        ("width", "100%"),
                        ("border-collapse", "separate"),
                        ("border-spacing", "0"),
                        ("border-radius", "12px"),
                        ("overflow", "hidden"),
                        ("font-size", "14px"),
                        ("background-color", "#0B1B34"),
                    ],
                },
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#16345B"),
                        ("color", "#FFFFFF"),
                        ("padding", "12px"),
                        ("text-align", "left"),
                        ("border", "1px solid #294568"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("background-color", "#0B1B34"),
                        ("color", "#EAF2FF"),
                        ("padding", "11px 12px"),
                        ("border", "1px solid #294568"),
                    ],
                },
                {
                    "selector": "tbody tr:nth-child(even) td",
                    "props": [("background-color", "#102440")],
                },
            ], overwrite=True)
            st.markdown(
                styled_anomaly_table.to_html(index=False),
                unsafe_allow_html=True,
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

    banking_file = PROJECT_ROOT / "data" / "domains" / "banking" / "banking_data.csv"

    try:
        banking_df = pd.read_csv(banking_file)
    except Exception as e:
        st.error(f"Unable to load banking dataset: {e}")
        return

    # Support the actual project CSV column names as well as normalized names.
    if "Transaction_Amount" not in banking_df.columns and "Amount" in banking_df.columns:
        banking_df["Transaction_Amount"] = banking_df["Amount"]
    if "Transaction_Type" not in banking_df.columns and "Type" in banking_df.columns:
        banking_df["Transaction_Type"] = banking_df["Type"]
    if "Branch" not in banking_df.columns:
        if "City" in banking_df.columns:
            banking_df["Branch"] = banking_df["City"]
        else:
            banking_df["Branch"] = "Unknown"
    if "Loan_Amount" not in banking_df.columns:
        banking_df["Loan_Amount"] = 0
    if "Date" not in banking_df.columns:
        banking_df["Date"] = pd.NaT

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
        fig.update_layout(xaxis_title="Date", yaxis_title="Transaction Amount")
        fig.update_traces(line=dict(color="#22D3EE", width=3), marker=dict(size=8, color="#A78BFA"), fill="tozeroy")
        st.plotly_chart(style_chart(fig, height=360, money_axis=True), use_container_width=True)

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
        fig.update_traces(marker_line_width=0, opacity=0.92, texttemplate="₹%{y:,.0f}", textposition="outside", cliponaxis=False)
        st.plotly_chart(style_chart(fig, height=360, money_axis=True), use_container_width=True)

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
        fig.update_traces(marker_line_width=0, opacity=0.92, texttemplate="₹%{y:,.0f}", textposition="outside", cliponaxis=False)
        st.plotly_chart(style_chart(fig, height=360, money_axis=True), use_container_width=True)

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
        fig.update_traces(marker_line_width=0, opacity=0.92, texttemplate="₹%{y:,.0f}", textposition="outside", cliponaxis=False)
        st.plotly_chart(style_chart(fig, height=360, money_axis=True), use_container_width=True)

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
        fig.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color="#0B1530", width=2)))
        st.plotly_chart(style_chart(fig, height=360), use_container_width=True)

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
        fig.update_traces(marker_line_width=0, opacity=0.92, texttemplate="₹%{y:,.0f}", textposition="outside", cliponaxis=False)
        st.plotly_chart(style_chart(fig, height=360, money_axis=True), use_container_width=True)

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
    # NEARBY BANK IDENTIFICATION
    # --------------------------------------------------------

    st.markdown("---")
    st.markdown("### 📍 Find Nearby Bank Branches")

    st.info(
        "Enter an area, city, location or PIN code to identify "
        "nearby bank branches and available branch details."
    )

    b1, b2 = st.columns(2)

    with b1:
        search_location = st.text_input(
            "📍 Enter Location / Area / City / PIN",
            placeholder="Example: Kadapa, Andhra Pradesh"
        )

    with b2:
        search_bank = st.text_input(
            "🏦 Bank Name (Optional)",
            placeholder="Example: SBI"
        )

    search_button = st.button(
        "🔎 Find Nearby Banks",
        type="primary",
        key="nearby_bank_search"
    )

    if search_button:

        if not search_location.strip():
            st.warning(
                "Please enter a location, area, city or PIN code."
            )

        else:

            with st.spinner(
                "Searching for nearby bank branches..."
            ):

                bank_results, search_info = search_nearby_banks(
                    search_location.strip(),
                    search_bank.strip()
                )

            if bank_results is None:

                st.error(
                    f"❌ {search_info}"
                )

            elif not bank_results:

                st.warning(
                    "No bank branches were found for the "
                    "entered location."
                )

            else:

                st.success(
                    f"✅ Found {len(bank_results)} bank branch(es) "
                    f"near the searched location."
                )

                if isinstance(search_info, dict):

                    st.caption(
                        f"📍 Search location: "
                        f"{search_info.get('location', search_location)}"
                    )

                # --------------------------------------------
                # Display bank cards
                # --------------------------------------------

                for index, bank in enumerate(bank_results):

                    st.markdown("---")

                    st.markdown(
                        f"#### 🏦 {bank['Bank Name']}"
                    )

                    c1, c2, c3 = st.columns(3)

                    c1.write(
                        f"**Branch:** "
                        f"{bank['Branch']}"
                    )

                    c2.write(
                        f"**Phone:** "
                        f"{bank['Phone']}"
                    )

                    c3.write(
                        f"**ATM:** "
                        f"{bank['ATM']}"
                    )

                    st.write(
                        f"📍 **Address:** "
                        f"{bank['Address']}"
                    )

                    st.write(
                        f"🕒 **Opening Hours:** "
                        f"{bank['Opening Hours']}"
                    )

                    st.write(
                        f"🛠️ **Services:** "
                        f"{bank['Services']}"
                    )

                    if bank["Website"] != "Not available":

                        st.markdown(
                            f"🌐 **Website:** "
                            f"[Open Website]({bank['Website']})"
                        )

                    if (
                        bank["Latitude"] is not None
                        and bank["Longitude"] is not None
                    ):

                        st.caption(
                            f"Coordinates: "
                            f"{bank['Latitude']}, "
                            f"{bank['Longitude']}"
                        )

    st.caption(
        "Bank branch information is obtained from "
        "OpenStreetMap public map data. "
        "Availability of phone numbers, hours and services "
        "depends on the mapped information."
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

    input_folder = PROJECT_ROOT / "realtime" / "input"
    files = [str(path) for path in input_folder.glob("*.csv")]

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

    # Support both the stream's Branch column and the static dataset's Class column.
    if "Branch" not in df.columns and "Class" in df.columns:
        df["Branch"] = df["Class"]
    if "Student_ID" not in df.columns and "StudentID" in df.columns:
        df["Student_ID"] = df["StudentID"]
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
    subject_chart_df = subject_analysis.sort_values("Average_Marks", ascending=True)
    fig = px.bar(subject_chart_df, x="Average_Marks", y="Subject", orientation="h", text="Average_Marks", color="Average_Marks", color_continuous_scale=["#8B5CF6", "#22D3EE", "#34D399"], title="Average marks by subject")
    fig.update_traces(texttemplate="%{text:.1f}/100", textposition="outside", cliponaxis=False, marker_line_width=0)
    fig.update_xaxes(range=[0, max(100, float(subject_chart_df["Average_Marks"].max()) * 1.15)])
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(style_chart(fig, height=340), use_container_width=True)

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
# PERSISTENT SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown("## 📊 Big Data Pipeline")
    st.caption("Navigate between all four domains")
    if st.button("🏠 Home / All Domains", key="nav_home", use_container_width=True):
        go_home()
        st.rerun()
    st.markdown("---")
    if st.button("🏥 Healthcare", key="nav_healthcare", use_container_width=True):
        open_domain("healthcare")
        st.rerun()
    if st.button("🛒 Retail", key="nav_retail", use_container_width=True):
        open_domain("retail")
        st.rerun()
    if st.button("🎓 Education", key="nav_education", use_container_width=True):
        open_domain("education")
        st.rerun()
    if st.button("🏦 Banking", key="nav_banking", use_container_width=True):
        open_domain("banking")
        st.rerun()

# ============================================================
# LOGIN / REGISTRATION AUTHENTICATION
# ============================================================
import csv
import hashlib
import hmac
import secrets

USERS_FILE = PROJECT_ROOT / "users.csv"
USER_FIELDS = ["Full_Name", "Username", "Email", "Password_Hash", "Salt"]


def load_users():
    if not USERS_FILE.exists():
        return []
    try:
        with USERS_FILE.open("r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except (OSError, csv.Error):
        return []


def save_user(full_name, username, email, password):
    users = load_users()
    if any(u.get("Username", "").casefold() == username.casefold() for u in users):
        return False, "That username is already registered. Please choose another."
    if any(u.get("Email", "").casefold() == email.casefold() for u in users):
        return False, "That email is already registered. Please log in instead."
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200000).hex()
    try:
        file_exists = USERS_FILE.exists()
        with USERS_FILE.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=USER_FIELDS)
            if not file_exists:
                writer.writeheader()
            writer.writerow({"Full_Name": full_name.strip(), "Username": username.strip(), "Email": email.strip(), "Password_Hash": password_hash, "Salt": salt})
        return True, "Account created successfully. You can now log in."
    except OSError:
        return False, "Could not save the account. Check the app's file permissions and try again."


def check_login(username, password):
    for user in load_users():
        if user.get("Username", "").casefold() == username.strip().casefold():
            salt = user.get("Salt", "")
            expected = user.get("Password_Hash", "")
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200000).hex()
            return hmac.compare_digest(actual, expected), user.get("Full_Name") or username
    return False, ""


def show_authentication():
    st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at 12% 10%, #142b52 0, #081326 38%, #050b16 100%); }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .auth-title { text-align:center; font-size:2.15rem; font-weight:800; color:#f4f8ff; margin:0.2rem 0; }
    .auth-subtitle { text-align:center; color:#9db5d8; margin-bottom:1.4rem; }
    .auth-pill { text-align:center; color:#65d8ff; font-size:.85rem; letter-spacing:2px; font-weight:700; }
    [data-testid="stForm"] { background:rgba(14,29,54,.92); border:1px solid #28476f; border-radius:18px; padding:1.3rem; }
    div[data-baseweb="tab-list"] { gap:8px; justify-content:center; }
    button[data-baseweb="tab"] { background:#10223e; border-radius:10px 10px 0 0; color:#dbeafe; padding:10px 24px; }
    button[data-baseweb="tab"][aria-selected="true"] { background:#164e82; color:white; }
    div.stButton > button[kind="primaryFormSubmit"], div.stButton > button[kind="primary"] { background:linear-gradient(90deg,#087cae,#6657d9); color:white; border:0; border-radius:10px; font-weight:700; }
    </style>
    <div class="auth-pill">BIG DATA • REAL-TIME • INTELLIGENCE</div>
    <div class="auth-title">Big Data Processing &amp; Analytics Pipeline</div>
    <div class="auth-subtitle">Sign in or create an account to explore all four analytics domains.</div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.15, 1])
    with center:
        login_tab, register_tab = st.tabs(["🔐 Login", "📝 Create Account"])
        with login_tab:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("### Welcome back")
                login_username = st.text_input("Username", key="login_username", placeholder="Enter your username")
                login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
                submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
                if submitted:
                    ok, full_name = check_login(login_username, login_password)
                    if ok:
                        st.session_state.authenticated = True
                        st.session_state.username = login_username.strip()
                        st.session_state.full_name = full_name
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
        with register_tab:
            with st.form("register_form", clear_on_submit=True):
                st.markdown("### Create your account")
                full_name = st.text_input("Full name", placeholder="Enter your full name")
                new_username = st.text_input("Username", placeholder="Choose a username")
                email = st.text_input("Email", placeholder="name@example.com")
                new_password = st.text_input("Password", type="password", placeholder="At least 8 characters")
                confirm_password = st.text_input("Confirm password", type="password", placeholder="Re-enter your password")
                registered = st.form_submit_button("Create Account", type="primary", use_container_width=True)
                if registered:
                    if not all([full_name.strip(), new_username.strip(), email.strip(), new_password, confirm_password]):
                        st.error("Please fill in all fields.")
                    elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
                        st.error("Please enter a valid email address.")
                    elif len(new_username.strip()) < 3:
                        st.error("Username must contain at least 3 characters.")
                    elif len(new_password) < 8:
                        st.error("Password must contain at least 8 characters.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        ok, message = save_user(full_name, new_username, email, new_password)
                        if ok:
                            st.success(message)
                        else:
                            st.error(message)
    st.markdown("<p style='text-align:center;color:#7892b8;font-size:.8rem;margin-top:1.5rem'>Secure password hashing enabled • Healthcare • Retail • Education • Banking</p>", unsafe_allow_html=True)


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "full_name" not in st.session_state:
    st.session_state.full_name = ""


# ============================================================
# ROUTER
# ============================================================
if not st.session_state.authenticated:
    show_authentication()
else:
    with st.sidebar:
        st.markdown(f"### 👋 Hello, {st.session_state.full_name or st.session_state.username}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.full_name = ""
            st.session_state.selected_domain = None
            st.rerun()
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
