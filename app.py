import streamlit as st
import pandas as pd

st.title("Consumers Used at Independent Time")

split_file = st.file_uploader("Upload Split Time.xlsx")
ind_file = st.file_uploader("Upload Independent Time.xlsx")

if split_file and ind_file:

    # Load sheets
    sk1 = pd.read_excel(split_file, sheet_name="Consumer (SK1)")
    sk2 = pd.read_excel(split_file, sheet_name="Consumer (SK2)")
    ind = pd.read_excel(ind_file)

    # Combine
    consumers = pd.concat([sk1, sk2], ignore_index=True)

    # Convert datetime
    consumers["OutageDateTime"] = pd.to_datetime(consumers["OutageDateTime"])

    results = []

    for _, row in ind.iterrows():

        if pd.isna(row["Date"]):
            continue

        timestamp = pd.to_datetime(str(row["Date"]) + " " + str(row["Independent Time"]))

        # Match same minute
        active = consumers[
            consumers["OutageDateTime"].dt.floor("min") == timestamp.floor("min")
        ]

        meter_list = active["Meterno"].astype(str).unique().tolist()

        results.append({
            "Date": row["Date"],
            "Time": row["Independent Time"],
            "Consumers Used": ", ".join(meter_list),
            "Number of Consumers": len(meter_list)
        })

    result_df = pd.DataFrame(results)

    st.subheader("Consumers Active at Independent Time")
    st.dataframe(result_df)

    st.download_button(
        "Download Results",
        result_df.to_csv(index=False),
        file_name="consumer_usage.csv"
    )
