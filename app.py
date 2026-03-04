import streamlit as st
import pandas as pd

st.title("Consumer Usage During Independent Time")

split_file = st.file_uploader("Upload Split Time.xlsx")
ind_file = st.file_uploader("Upload Independent Time.xlsx")

if split_file and ind_file:

    sk1 = pd.read_excel(split_file, sheet_name="Consumer (SK1)")
    sk2 = pd.read_excel(split_file, sheet_name="Consumer (SK2)")
    ind = pd.read_excel(ind_file)

    # Add consumer source
    sk1["Consumer Source"] = "SK1"
    sk2["Consumer Source"] = "SK2"

    consumers = pd.concat([sk1, sk2], ignore_index=True)

    consumers["OutageDateTime"] = pd.to_datetime(consumers["OutageDateTime"])
    consumers["RestoreDateTime"] = pd.to_datetime(consumers["RestoreDateTime"])

    results = []

    for _, row in ind.iterrows():

        if pd.isna(row["Date"]):
            continue

        timestamp = pd.to_datetime(str(row["Date"]) + " " + str(row["Independent Time"]))

        active = consumers[
            (consumers["OutageDateTime"] <= timestamp) &
            (consumers["RestoreDateTime"] >= timestamp)
        ]

        # Use actual consumer names
        consumer_names = active["Consumer"].astype(str).tolist()

        results.append({
            "Date": row["Date"],
            "Time": row["Independent Time"],
            "Consumers Used": ", ".join(consumer_names),
            "Number of Consumers": len(consumer_names)
        })

    result_df = pd.DataFrame(results)

    st.subheader("Consumers Used at Independent Time")

    st.dataframe(result_df)

    st.download_button(
        "Download Result",
        result_df.to_csv(index=False),
        file_name="consumer_usage_results.csv"
    )
