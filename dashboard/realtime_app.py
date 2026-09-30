
import streamlit as st
import pandas as pd
import os
import glob
from datetime import datetime

st.set_page_config(
    page_title="Real-Time Student Analytics",
    page_icon="📊",
    layout="wide"
)

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
