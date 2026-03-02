import streamlit as st
import pandas as pd

st.set_page_config(page_title="Independent Time Generator", layout="wide")

st.title("⚡ Independent Time - Selected January Day")

uploaded_file = st.file_uploader("Upload Split Time Excel File", type=["xlsx"])

if uploaded_file:

    try:
        # Read DT sheet
        df = pd.read_excel(uploaded_file, sheet_name="DT")

        # Keep only required columns
        df = df[["Meterno", "OutageDateTime", "OutageDuration"]]

        # Convert datetime
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

        # Extract components
        df["Day"] = df["OutageDateTime"].dt.day
        df["Time"] = df["OutageDateTime"].dt.time

        # Day selector
        available_days = sorted(df["Day"].unique())
        selected_day = st.selectbox("Select January Day", available_days)

        df_day = df[df["Day"] == selected_day]

        results = []

        # Group by meter only (since single day selected)
        grouped = df_day.groupby("Meterno")

        for meter, group in grouped:

            # Count outage duration frequency
            duration_counts = group["OutageDuration"].value_counts()

            # Unique durations
            unique_durations = duration_counts[duration_counts == 1].index.tolist()

            if unique_durations:
                selected_row = group[group["OutageDuration"] == unique_durations[0]].iloc[0]
            else:
                selected_row = group.loc[group["OutageDuration"].idxmax()]

            results.append({
                "Meterno": meter,
                "Independent Time": selected_row["Time"],
                "OutageDuration": selected_row["OutageDuration"]
            })

        result_df = pd.DataFrame(results).sort_values("Meterno")

        st.subheader(f"📊 Independent Times for January {selected_day}")
        st.dataframe(result_df, use_container_width=True)

        st.download_button(
            label="⬇ Download CSV",
            data=result_df.to_csv(index=False).encode("utf-8"),
            file_name=f"Independent_Time_Jan_{selected_day}.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error processing file: {e}")

else:
    st.info("Please upload the Excel file to begin.")
