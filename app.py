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

    # Create timestamp column
    ind["Timestamp"] = pd.to_datetime(
        ind["Date"].astype(str) + " " + ind["Independent Time"].astype(str)
    )

    results = []

    for _, row in ind.iterrows():

        ts = row["Timestamp"]

        active = consumers[
            consumers["OutageDateTime"].dt.floor("min") == ts.floor("min")
        ]

        meters = active["Meterno"].astype(str).unique().tolist()

        results.append({
            "Date": ts.date(),
            "Time": ts.time(),
            "Consumers": meters,
            "Count": len(meters)
        })

    result_df = pd.DataFrame(results)

    # Display grouped by day
    for date, group in result_df.groupby("Date"):

        st.subheader(f"Date: {date}")

        for _, r in group.iterrows():

            st.write(f"Time: {r['Time']}")
            st.write(f"Consumers ({r['Count']}):")

            if r["Consumers"]:
                st.write(", ".join(r["Consumers"]))
            else:
                st.write("No consumers found")

            st.divider()
