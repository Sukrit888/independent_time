import streamlit as st
import pandas as pd

st.set_page_config(page_title="Independent Time Generator", layout="wide")

st.title("⚡ Independent Time - Selected January Day")

uploaded_file = st.file_uploader("Upload Split Time Excel File", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file, sheet_name="DT")
    df = df[["Meterno", "OutageDateTime", "OutageDuration"]]

    df["OutageDateTime"] = pd.to_datetime(df["OutageDateTime"], errors="coerce")
    df = df.dropna(subset=["OutageDateTime"])

    # Filter January and remove zero duration
    df = df[
        (df["OutageDateTime"].dt.month == 1) &
        (df["OutageDuration"] > 0)
    ]

    if df.empty:
        st.warning("No valid January outage data found.")
        st.stop()

    df["Day"] = df["OutageDateTime"].dt.day
    df["Time"] = df["OutageDateTime"].dt.time

    selected_day = st.selectbox(
        "Select January Day",
        sorted(df["Day"].unique())
    )

    # Filter only selected day
    df_day = df[df["Day"] == selected_day].copy()

    if df_day.empty:
        st.warning("No data for selected day.")
        st.stop()

    # -------------------------------
    # STEP 1: Find unique TIME
    # -------------------------------
    time_counts = df_day["Time"].value_counts()
    unique_times = time_counts[time_counts == 1].index

    if len(unique_times) > 0:
        candidate = df_day[df_day["Time"].isin(unique_times)]
        selected_row = candidate.loc[candidate["OutageDuration"].idxmax()]

    else:
        # -------------------------------
        # STEP 2: Find unique DURATION
        # -------------------------------
        duration_counts = df_day["OutageDuration"].value_counts()
        unique_durations = duration_counts[duration_counts == 1].index

        if len(unique_durations) > 0:
            candidate = df_day[df_day["OutageDuration"].isin(unique_durations)]
            selected_row = candidate.loc[candidate["OutageDuration"].idxmax()]
        else:
            # -------------------------------
            # STEP 3: Fallback max duration
            # -------------------------------
            selected_row = df_day.loc[df_day["OutageDuration"].idxmax()]

    # ✅ Create ONE ROW dataframe only
    result = pd.DataFrame({
        "Meterno": [selected_row["Meterno"]],
        "Independent Time": [selected_row["Time"]],
        "OutageDuration": [selected_row["OutageDuration"]]
    })

    st.subheader(f"📊 Independent Time for January {selected_day}")
    st.table(result)   # table ensures exactly what is passed is shown

else:
    st.info("Please upload the Excel file to begin.")
