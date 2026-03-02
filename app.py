import streamlit as st
import pandas as pd

st.set_page_config(page_title="Independent Time Generator", layout="wide")

st.title("⚡ Independent Time Generator - January (DT Sheet Only)")

st.markdown("""
**Logic Applied:**
1. Ignore rows where Outage Duration = 0  
2. First preference → Unique Time for that day  
3. Second preference → Highest Outage Duration  
4. Output includes Meter Number  
""")

uploaded_file = st.file_uploader("Upload Split Time Excel File", type=["xlsx"])

if uploaded_file:

    try:
        # Read DT sheet
        df = pd.read_excel(uploaded_file, sheet_name="DT")

        # Standardize column names (strip spaces)
        df.columns = df.columns.str.strip()

        required_columns = ["Meter Number", "Date", "Time", "Outage Duration"]

        if not all(col in df.columns for col in required_columns):
            st.error("DT sheet must contain columns: Meter Number, Date, Time, Outage Duration")
            st.stop()

        # Convert Date to datetime
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Filter January only
        df = df[df["Date"].dt.month == 1]

        # Remove zero outage duration
        df = df[df["Outage Duration"] > 0]

        if df.empty:
            st.warning("No valid January outage data found.")
            st.stop()

        df = df[required_columns]

        results = []

        # Group by Meter and Date
        grouped = df.groupby(["Meter Number", "Date"])

        for (meter, date), group in grouped:

            # Count time frequency
            time_counts = group["Time"].value_counts()

            # Unique times
            unique_times = time_counts[time_counts == 1].index.tolist()

            if unique_times:
                selected_row = group[group["Time"] == unique_times[0]].iloc[0]
            else:
                selected_row = group.loc[group["Outage Duration"].idxmax()]

            results.append({
                "Meter Number": meter,
                "Date": date.date(),
                "Independent Time": selected_row["Time"],
                "Outage Duration": selected_row["Outage Duration"]
            })

        result_df = pd.DataFrame(results)
        result_df = result_df.sort_values(["Meter Number", "Date"])

        st.subheader("📊 Independent Time Output - January")
        st.dataframe(result_df, use_container_width=True)

        # Download option
        st.download_button(
            label="⬇ Download Output as Excel",
            data=result_df.to_csv(index=False).encode("utf-8"),
            file_name="Independent_Time_January.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error processing file: {e}")

else:
    st.info("Please upload the Excel file to begin.")
