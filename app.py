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

    consumers["OutageDateTime"] = pd.to_datetime(consumers["OutageDateTime"])
    consumers["RestoreDateTime"] = pd.to_datetime(consumers["RestoreDateTime"])

    # Load independent time file
    ind = pd.read_excel(ind_file)
    ind["Date"] = pd.to_datetime(ind["Date"])

    counts = []
    lists = []

    for _, row in ind.iterrows():

        timestamp = row["Date"] + pd.to_timedelta(str(row["Independent Time"]))

        active = consumers[
            (consumers["OutageDateTime"] <= timestamp) &
            (consumers["RestoreDateTime"] >= timestamp)
        ]

        meter_list = active["Meterno"].astype(str).unique().tolist()

        counts.append(len(meter_list))
        lists.append(", ".join(meter_list))

    ind["Number of consumers affected"] = counts
    ind["List of consumers"] = lists

    st.subheader("Result Table")
    st.dataframe(ind)

    # Show consumers clearly for each time
    st.subheader("Consumers by Time")

    for _, row in ind.iterrows():

        st.write(f"### {row['Date'].date()} — {row['Independent Time']}")
        st.write(f"Consumers affected: {row['Number of consumers affected']}")

        if row["List of consumers"]:
            st.write(row["List of consumers"])
        else:
            st.write("No consumers affected")

        st.divider()

    # Download Excel
    output_file = "independent_time_result.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        ind.to_excel(writer, index=False)

    with open(output_file, "rb") as f:
        st.download_button(
            "Download Updated Excel",
            f,
            file_name="independent_time_result.xlsx"
        )
