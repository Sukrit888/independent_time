import streamlit as st
import pandas as pd

st.title("Consumers Used at Independent Times")

split_file = st.file_uploader("Upload Split Time.xlsx")
ind_file = st.file_uploader("Upload Independent Time.xlsx")

if split_file and ind_file:

    # Load sheets
    sk1 = pd.read_excel(split_file, sheet_name="Consumer (SK1)")
    sk2 = pd.read_excel(split_file, sheet_name="Consumer (SK2)")
    ind = pd.read_excel(ind_file)

    consumers = pd.concat([sk1, sk2], ignore_index=True)

    consumers["OutageDateTime"] = pd.to_datetime(consumers["OutageDateTime"])

    results = []

    for _, row in ind.iterrows():

        if pd.isna(row["Date"]):
            continue

        timestamp = pd.to_datetime(str(row["Date"]) + " " + str(row["Independent Time"]))

        active = consumers[
            consumers["OutageDateTime"].dt.floor("min") == timestamp.floor("min")
        ]

        meter_list = active["Meterno"].astype(str).unique().tolist()

        results.append({
            "Date": row["Date"],
            "Time": row["Independent Time"],
            "Consumers": meter_list,
            "Count": len(meter_list)
        })

    result_df = pd.DataFrame(results)

    # Display grouped by date
    for date in result_df["Date"].unique():

        st.subheader(f"Date: {date}")

        day_df = result_df[result_df["Date"] == date]

        for _, r in day_df.iterrows():

            st.write(f"Time: {r['Time']}")
            st.write(f"Consumers ({r['Count']}):")

            st.write(", ".join(r["Consumers"]))
            st.divider()
