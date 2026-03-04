import streamlit as st
import pandas as pd

st.title("Consumers Used at Independent Times")

split_file = st.file_uploader("Upload Split Time.xlsx")
ind_file = st.file_uploader("Upload Independent Time.xlsx")

if split_file and ind_file:

    sk1 = pd.read_excel(split_file, sheet_name="Consumer (SK1)")
    sk2 = pd.read_excel(split_file, sheet_name="Consumer (SK2)")

    consumers = pd.concat([sk1, sk2], ignore_index=True)

    consumers["OutageDateTime"] = pd.to_datetime(consumers["OutageDateTime"])

    ind = pd.read_excel(ind_file)
    ind["Date"] = pd.to_datetime(ind["Date"])

    results = []

    for _, row in ind.iterrows():

        timestamp = row["Date"] + pd.to_timedelta(str(row["Independent Time"]))

        duration = row["Outage Duration"]

        window_end = timestamp + pd.Timedelta(minutes=duration)

        active = consumers[
            (consumers["OutageDateTime"] >= timestamp) &
            (consumers["OutageDateTime"] <= window_end)
        ]

        meters = active["Meterno"].astype(str).unique().tolist()

        results.append({
            "Date": timestamp.date(),
            "Time": timestamp.strftime("%H:%M"),
            "Consumers": meters,
            "Count": len(meters)
        })

    result_df = pd.DataFrame(results)

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
