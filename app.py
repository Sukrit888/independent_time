import streamlit as st
import pandas as pd

st.set_page_config(page_title="Independent Time Generator", layout="wide")

st.title("⚡ Independent Time Generator - January (DT Sheet)")

st.markdown("""
**Logic Applied:**
1. Ignore OutageDuration = 0  
2. First preference → Unique OutageDuration  
3. Second preference → Highest OutageDuration  
4. Output includes Meterno  
""")

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

        # Filter January
        df = df[df["OutageDateTime"].dt.month == 1]

        # Remove zero duration
        df = df[df["OutageDuration"] > 0]

        if df.empty:
            st.warning("No valid January outage data found.")
            st.stop()

        # Extract Date, Time, Day
        df["Date"] = df["OutageDateTime"].dt.date
        df["Time"] = df["OutageDateTime"].dt.time
        df["Day"] = df["OutageDateTime"].dt.day

        # User selects day
        available_days = sorted(df["Day"].unique())
        selected_day = st.selectbox("Select January Day", available_days)

        df_day = df[df["Day"] == selected_day]

        results = []

        grouped = df_day.groupby(["Meterno", "Date"])

        for (meter, date), group in grouped:

            # Count frequency of outage durations
            duration_counts = group["OutageDuration"].value_counts()

            # Find unique durations
            unique_durations = duration_counts[duration_counts == 1].index.tolist()

            if unique_durations:
                # Select row with that unique duration
                selected_row = group[group["OutageDuration"] == unique_durations[0]].iloc[0]
            else:
                # Select max duration
                selected_row = group.loc[group["OutageDuration"].idxmax()]

            results.append({
                "Meterno": meter,
                "Date": date,
                "Independent Time": selected_row["Time"],
                "OutageDuration": selected_row["OutageDuration"]
            })

        result_df = pd.DataFrame(results)
        result_df = result_df.sort_values("Meterno")

        st.subheader(f"📊 Independent Time Output - January {selected_day}")
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
