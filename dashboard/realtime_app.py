
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import os
import glob
from datetime import datetime

st.set_page_config(
    page_title="Real-Time Student Analytics",
    page_icon="📊",
    layout="wide"
)

st_autorefresh(interval=3000, key="realtime_refresh")

st.title("📊 Real-Time Student Analytics Dashboard")
st.subheader("Live Education Data Processing & Intelligent Insights")

input_folder = "/content/big_data_project/realtime/input"

files = glob.glob(os.path.join(input_folder, "*.csv"))

if files:

    dataframes = []

    for file in files:
        try:
            df = pd.read_csv(file)
            dataframes.append(df)
        except:
            pass

    if dataframes:

        df = pd.concat(dataframes, ignore_index=True)

        # Basic statistics
        total_records = len(df)
        average_marks = df["Marks"].mean()
        average_attendance = df["Attendance"].mean()
        top_marks = df["Marks"].max()

        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "📥 Live Records",
            total_records
        )

        col2.metric(
            "📈 Average Marks",
            f"{average_marks:.2f}"
        )

        col3.metric(
            "🏆 Top Marks",
            top_marks
        )

        col4.metric(
            "📅 Avg Attendance",
            f"{average_attendance:.2f}%"
        )

        st.divider()

        # Anomaly detection
        df["Anomaly"] = "Normal"

        df.loc[
            (df["Marks"] < 50) &
            (df["Attendance"] < 70),
            "Anomaly"
        ] = "High Risk"

        df.loc[
            (df["Marks"] < 50) &
            (df["Attendance"] >= 70),
            "Anomaly"
        ] = "Low Marks"

        df.loc[
            (df["Marks"] >= 50) &
            (df["Attendance"] < 70),
            "Anomaly"
        ] = "Low Attendance"

        anomalies = df[df["Anomaly"] != "Normal"]

        st.subheader("⚠️ Automatic Anomaly Detection")

        if len(anomalies) > 0:
            st.dataframe(
                anomalies[
                    [
                        "Student_ID",
                        "Branch",
                        "Subject",
                        "Marks",
                        "Attendance",
                        "Anomaly"
                    ]
                ],
                use_container_width=True
            )
        else:
            st.success("No anomalies detected.")

        st.divider()

        # Subject-wise analysis
        st.subheader("📚 Subject-wise Performance")

        subject_analysis = df.groupby("Subject").agg(
            Average_Marks=("Marks", "mean"),
            Average_Attendance=("Attendance", "mean"),
            Records=("Student_ID", "count")
        ).reset_index()

        st.dataframe(
            subject_analysis,
            use_container_width=True
        )

        st.bar_chart(
            subject_analysis.set_index("Subject")["Average_Marks"]
        )

        st.divider()

        # Automatic insights
        st.subheader("💡 Automatic Insights")

        if average_marks >= 80:
            st.success(
                "Overall performance is excellent."
            )
        elif average_marks >= 60:
            st.info(
                "Overall performance is moderate."
            )
        else:
            st.warning(
                "Overall performance needs improvement."
            )

        if average_attendance < 70:
            st.warning(
                "Average attendance is below 70%."
            )
        else:
            st.success(
                "Average attendance is satisfactory."
            )

        top_student = df.loc[
            df["Marks"].idxmax()
        ]

        st.info(
            f"🏆 Highest recorded marks: "
            f"{top_student['Marks']} "
            f"({top_student['Student_ID']} - "
            f"{top_student['Subject']})"
        )

        st.caption(
            f"Last dashboard update: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    else:
        st.warning("No readable data available.")

else:
    st.warning("Waiting for real-time data...")


# ============================================================
# HEALTHCARE ANALYTICS
# ============================================================

st.markdown("---")
st.header("🏥 Healthcare Analytics")

healthcare_file = "/content/big_data_project/data/domains/healthcare/healthcare_data.csv"

try:
    healthcare_df = pd.read_csv(healthcare_file)

    # Automatic risk detection
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
    high_risk = (healthcare_df["Risk_Status"] == "HIGH RISK").sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Patients", total_patients)
    col2.metric("Total Treatment Cost", f"₹{total_cost:,.0f}")
    col3.metric("Average Age", f"{average_age:.1f}")
    col4.metric("Average Visits", f"{average_visits:.2f}")
    col5.metric("High-Risk Patients", high_risk)

    st.subheader("🏥 Department-wise Treatment Cost")

    department_health = healthcare_df.groupby(
        "Department"
    )["Treatment_Cost"].sum().reset_index()

    st.bar_chart(
        department_health.set_index("Department")
    )

    st.subheader("⚠️ Automatic Risk Detection")

    risk_data = healthcare_df[
        healthcare_df["Risk_Status"] != "NORMAL"
    ]

    if len(risk_data) > 0:
        st.dataframe(
            risk_data[
                [
                    "Patient_ID",
                    "Department",
                    "Visits",
                    "Treatment_Cost",
                    "Length_of_Stay",
                    "Risk_Status"
                ]
            ],
            use_container_width=True
        )
    else:
        st.success("No high-risk or attention-required records detected.")

    st.subheader("💡 Automatic Healthcare Insights")

    if high_risk > 0:
        st.warning(
            f"{high_risk} high-risk patient record(s) detected automatically."
        )

    if healthcare_df["Treatment_Cost"].max() >= 50000:
        st.info(
            "High treatment-cost cases require additional attention."
        )

    if healthcare_df["Length_of_Stay"].mean() < 5:
        st.info(
            "Average hospital stay is relatively short."
        )

except Exception as e:
    st.error(f"Healthcare analytics error: {e}")





# ============================================================
# WEB-BASED HOSPITAL DATA ANALYSIS
# ============================================================

st.markdown("---")
st.header("🏥 Web-Based Hospital Data Analysis")

st.write(
    "Search a hospital name to retrieve publicly available "
    "hospital information from the web."
)

hospital_name = st.text_input(
    "Enter Hospital Name",
    placeholder="Example: RIMS General Hospital"
)

if st.button("🔎 Search Hospital Details"):

    if hospital_name.strip():

        import requests

        search_api = "https://nominatim.openstreetmap.org/search"

        params = {
            "q": hospital_name.strip(),
            "format": "json",
            "addressdetails": 1,
            "limit": 5
        }

        headers = {
            "User-Agent": "BigDataAnalyticsDashboard/1.0"
        }

        try:

            response = requests.get(
                search_api,
                params=params,
                headers=headers,
                timeout=15
            )

            results = response.json()

            if results:

                st.success(
                    f"{len(results)} web result(s) found."
                )

                selected = results[0]

                display_name = selected.get(
                    "display_name",
                    hospital_name
                )

                latitude = selected.get("lat", "Not available")
                longitude = selected.get("lon", "Not available")

                address = selected.get(
                    "address",
                    {}
                )

                # ------------------------------------------------
                # HOSPITAL DETAILS
                # ------------------------------------------------

                st.subheader("🏥 Hospital Details")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Hospital Name",
                        hospital_name
                    )

                    st.write(
                        "**📍 Location:**",
                        display_name
                    )

                with col2:
                    st.write(
                        "**🌐 Data Source:** OpenStreetMap"
                    )

                    st.write(
                        "**🏷️ Place Type:**",
                        selected.get(
                            "type",
                            "Not available"
                        )
                    )

                # ------------------------------------------------
                # ADDRESS DETAILS
                # ------------------------------------------------

                st.subheader("📍 Address Information")

                address_data = {
                    "House / Building": address.get(
                        "house_number",
                        "Not available"
                    ),
                    "Road": address.get(
                        "road",
                        "Not available"
                    ),
                    "Area": address.get(
                        "suburb",
                        address.get(
                            "neighbourhood",
                            "Not available"
                        )
                    ),
                    "City": address.get(
                        "city",
                        address.get(
                            "town",
                            address.get(
                                "village",
                                "Not available"
                            )
                        )
                    ),
                    "District": address.get(
                        "county",
                        "Not available"
                    ),
                    "State": address.get(
                        "state",
                        "Not available"
                    ),
                    "Country": address.get(
                        "country",
                        "Not available"
                    ),
                    "Postal Code": address.get(
                        "postcode",
                        "Not available"
                    )
                }

                address_df = __import__(
                    "pandas"
                ).DataFrame(
                    list(address_data.items()),
                    columns=["Field", "Value"]
                )

                st.dataframe(
                    address_df,
                    use_container_width=True,
                    hide_index=True
                )

                # ------------------------------------------------
                # COORDINATES
                # ------------------------------------------------

                st.subheader("🗺️ Geographic Information")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Latitude",
                        latitude
                    )

                with col2:
                    st.metric(
                        "Longitude",
                        longitude
                    )

                try:

                    map_df = __import__(
                        "pandas"
                    ).DataFrame({
                        "latitude": [
                            float(latitude)
                        ],
                        "longitude": [
                            float(longitude)
                        ]
                    })

                    st.map(map_df)

                except Exception:
                    pass

                # ------------------------------------------------
                # ALL SEARCH RESULTS
                # ------------------------------------------------

                if len(results) > 1:

                    st.subheader(
                        "🔎 Other Matching Hospital Results"
                    )

                    other_results = []

                    for item in results:

                        other_results.append({
                            "Name": item.get(
                                "display_name",
                                "Not available"
                            ),
                            "Type": item.get(
                                "type",
                                "Not available"
                            ),
                            "Latitude": item.get(
                                "lat",
                                "Not available"
                            ),
                            "Longitude": item.get(
                                "lon",
                                "Not available"
                            )
                        })

                    other_df = __import__(
                        "pandas"
                    ).DataFrame(
                        other_results
                    )

                    st.dataframe(
                        other_df,
                        use_container_width=True,
                        hide_index=True
                    )

                # ------------------------------------------------
                # AUTOMATIC WEB DATA INSIGHT
                # ------------------------------------------------

                st.subheader(
                    "💡 Automatic Hospital Data Insight"
                )

                st.info(
                    f"The web search identified "
                    f"{len(results)} matching location record(s) "
                    f"for '{hospital_name}'. The dashboard "
                    f"automatically extracted the available "
                    f"location and geographic information."
                )

            else:

                st.warning(
                    "No matching hospital data found on the web."
                )

        except Exception as e:

            st.error(
                f"Hospital web data error: {e}"
            )

    else:

        st.warning(
            "Please enter a hospital name."
        )
