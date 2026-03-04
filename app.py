import streamlit as st
import pandas as pd

st.title("Independent Time Consumer Analyzer")

split_file = st.file_uploader("Upload Split Time.xlsx")
ind_file = st.file_uploader("Upload Independent Time.xlsx")

if split_file and ind_file:

    # Load consumer sheets
    sk1 = pd.read_excel(split_file, sheet_name="Consumer (SK1)")
    sk2 = pd.read_excel(split_file, sheet_name="Consumer (SK2)")

    consumers = pd.concat([sk1, sk2], ignore_index=True)

    # Convert datetime
    consumers["OutageDateTime"] = pd.to_datetime(consumers["OutageDateTime"])
    consumers["RestoreDateTime"] = pd.to_datetime(consumers["RestoreDateTime"])

    # Load independent times
    ind = pd.read_excel(ind_file)

    ind["Date"] = pd.to_datetime(ind["Date"])

    results_counts = []
    results_lists = []

    for _, row in ind.iterrows():

        timestamp = row["Date"] + pd.to_timedelta(str(row["Independent Time"]))

        active = consumers[
            (consumers["OutageDateTime"] <= timestamp) &
            (consumers["RestoreDateTime"] >= timestamp)
        ]

        meters = active["Meterno"].astype(str).unique().tolist()

        results_counts.append(len(meters))
        results_lists.append(", ".join(meters))

    # Add results to dataframe
    ind["Number of consumers affected"] = results_counts
    ind["List of consumers"] = results_lists

    st.subheader("Processed Output")
    st.dataframe(ind)

    # Excel download
    output_file = "independent_time_result.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        ind.to_excel(writer, index=False)

    with open(output_file, "rb") as f:
        st.download_button(
            label="Download Updated Excel",
            data=f,
            file_name="independent_time_result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
