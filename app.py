import streamlit as st
import pandas as pd

st.set_page_config(page_title="Independent Time Generator", layout="wide")

st.title("⚡ Independent Time - Selected January Day")

uploaded_file = st.file_uploader("Upload Split Time Excel File", type=["xlsx"])

if uploaded_file:

    try:
        df = pd.read_excel(uploaded_file, sheet_name="DT")
        df = df[["Meterno", "OutageDateTime", "OutageDuration"]]

        df["OutageDateTime"] = pd.to_datetime(df["OutageDateTime"], errors="coerce")
        df = df.dropna(subset=["OutageDateTime"])

        # Filter January & remove zero duration
        df = df[
            (df["OutageDateTime"].dt.month == 1) &
            (df["OutageDuration"] > 0)
        ]

        if df.empty:
            st.warning("No valid January outage data found.")
            st.stop()

        df["Day"] = df["OutageDateTime"].dt.day
        df["Time"] = df["OutageDateTime"].dt.time

        available_days = sorted(df["Day"].unique())
        selected_day = st.selectbox("Select January Day", available_days)

        df_day = df[df["Day"] == selected_day]

        if df_day.empty:
            st.warning("No data for selected day.")
            st.stop()

        # ---------------------------
        # STEP 1 → Unique Time
        # ---------------------------
        time_counts = df_day["Time"].value_counts()
        unique_times = time_counts[time_counts == 1].index.tolist()

        if unique_times:
            # If multiple unique times → choose one with max duration
            candidate_rows = df_day[df_day["Time"].isin(unique_times)]
            selected_row = candidate_rows.loc[candidate_rows["OutageDuration"].idxmax()]

        else:
            # ---------------------------
            # STEP 2 → Unique Duration
            # ---------------------------
            duration_counts = df_day["OutageDuration"].value_counts()
            unique_durations = duration_counts[duration_counts == 1].index.tolist()

            if unique_durations:
                selected_duration = max(unique_durations)
                selected_row = df_day[df_day["OutageDuration"] == selected_duration].iloc[0]
            else:
                # ---------------------------
                # STEP 3 → Fallback Max Duration
                # ---------------------------
                selected_row = df_day.loc[df_day["OutageDuration"].idxmax()]

        result = pd.DataFrame([{
            "Meterno": selected_row["Meterno"],
            "Independent Time": selected_row["Time"],
            "OutageDuration": selected_row["OutageDuration"]
        }])

        st.subheader(f"📊 Independent Time for January {selected_day}")
        st.dataframe(result, use_container_width=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")

else:
    st.info("Please upload the Excel file to begin.")
