import streamlit as st
import pandas as pd

st.set_page_config(page_title="Power Outage Tracker", layout="wide")

st.title("⚡ SK1 Consumer Outage Tracker")
st.markdown("This app matches the reference times with the January outage intervals.")

# File uploaders
with st.sidebar:
    st.header("Upload Files")
    time_file = st.file_uploader("Upload Independent Time File", type=['csv', 'xlsx'])
    melli_file = st.file_uploader("Upload Power outage Melli File", type=['csv', 'xlsx'])

if time_file and melli_file:
    try:
        # Load Reference Times
        if time_file.name.endswith('.csv'):
            df_ind = pd.read_csv(time_file)
        else:
            df_ind = pd.read_excel(time_file)

        # Load Melli Data (Targeting January Sheet)
        if melli_file.name.endswith('.xlsx'):
            df_melli = pd.read_excel(melli_file, sheet_name='January')
        else:
            df_melli = pd.read_csv(melli_file)

        # Clean and Convert Timestamps
        df_melli['OutageDateTime'] = pd.to_datetime(df_melli['OutageDateTime'])
        df_melli['RestoreDateTime'] = pd.to_datetime(df_melli['RestoreDateTime'])
        
        # Filter Melli data for only SK1 consumers once to save speed
        df_sk1 = df_melli[df_melli['Meterno'].astype(str).str.startswith('SK1')].copy()

        results = []

        # Iterate through each reference time in the Independent Time file
        for index, row in df_ind.iterrows():
            # Combine Date and Independent Time into one timestamp
            date_part = str(row['Date']).split(' ')[0]
            time_part = str(row['Independent Time'])
            target_ts = pd.to_datetime(f"{date_part} {time_part}")

            # LOGIC: Find rows where target_ts is BETWEEN Outage and Restore
            # Example: Is 08:53:00 between 08:50:00 and 09:00:00?
            mask = (df_sk1['OutageDateTime'] <= target_ts) & (df_sk1['RestoreDateTime'] >= target_ts)
            
            # Get the matches
            matched_consumers = df_sk1[mask]['Meterno'].unique().tolist()
            
            results.append({
                "Date": date_part,
                "Ref Time": time_part,
                "No. of Consumers": len(matched_consumers),
                "Consumer List": ", ".join(matched_consumers)
            })

        # Display output
        output_df = pd.DataFrame(results)
        st.subheader("Results Table")
        st.dataframe(output_df, use_container_width=True)

        # Download CSV
        csv = output_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results as CSV", csv, "outage_analysis.csv", "text/csv")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Check that your column names match: 'Date', 'Independent Time', 'Meterno', 'OutageDateTime', 'RestoreDateTime'")
else:
    st.info("Waiting for both files to be uploaded...")
