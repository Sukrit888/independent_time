import streamlit as st
import pandas as pd
from datetime import timedelta

st.title("Consumer Usage Detection")

st.write("Identify which consumers were active during independent outage times.")

split_file = st.file_uploader("Upload Split Time.xlsx")
ind_file = st.file_uploader("Upload Independent Time.xlsx")

if split_file and ind_file:

    sk1 = pd.read_excel(split_file, sheet_name="Consumer (SK1)")
    sk2 = pd.read_excel(split_file, sheet_name="Consumer (SK2)")
    independent = pd.read_excel(ind_file)

    sk1['Consumer'] = "SK1"
    sk2['Consumer'] = "SK2"

    consumers = pd.concat([sk1, sk2])

    consumers['OutageDateTime'] = pd.to_datetime(consumers['OutageDateTime'])
    consumers['RestoreDateTime'] = pd.to_datetime(consumers['RestoreDateTime'])

    results = []

    for _, row in independent.iterrows():

        if pd.isna(row['Date']):
            continue

        start_time = pd.to_datetime(str(row['Date']) + " " + str(row['Independent Time']))
        end_time = start_time + timedelta(minutes=row['Outage Duration'])

        mask = (
            (consumers['OutageDateTime'] <= end_time) &
            (consumers['RestoreDateTime'] >= start_time)
        )

        matched = consumers[mask]

        consumer_list = matched['Consumer'].tolist()

        results.append({
            "Date": row['Date'],
            "Independent Time": row['Independent Time'],
            "Consumers Used": ", ".join(consumer_list)
        })

    result_df = pd.DataFrame(results)

    st.subheader("Consumers Active During Independent Time")

    st.dataframe(result_df)

    st.download_button(
        "Download Results",
        result_df.to_csv(index=False),
        file_name="consumer_usage.csv"
    )
