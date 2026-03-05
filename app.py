import streamlit as st
import pandas as pd

st.set_page_config(page_title="Power Outage Tracker", layout="wide")

st.title("⚡ Power Outage Consumer Analysis")
st.info("Upload your files below. Data is processed in your browser and not stored on GitHub.")

# Sidebar for file uploads
with st.sidebar:
    st.header("1. Upload Data")
    # Independent Time file
    time_file = st.file_uploader("Upload Independent Time File", type=['csv', 'xlsx'])
    # Power outage Melli file (January data)
    melli_file = st.file_uploader("Upload Power outage Melli (January)", type=['csv', 'xlsx'])

if time_file and melli_file:
    try:
        # Load Data
        df_ind = pd.read_csv(time_file) if time_file.name.endswith('.csv') else pd.read_excel(time_file)
        df_melli = pd.read_csv(melli_file) if melli_file.name.endswith('.csv') else pd.read_excel(melli_file)

        # Convert Melli timestamps
        df_melli['OutageDateTime'] = pd.to_datetime(df_melli['OutageDateTime'])
        df_melli['RestoreDateTime'] = pd.to_datetime(df_melli['RestoreDateTime'])
        
        results = []

        # Progress bar for better UX
        progress_bar = st.progress(0)
        total_rows = len(df_ind)

        for i, row in df_ind.iterrows():
            # Extract Date and Time from Independent Time file
            d_str = str(row['Date']).split(' ')[0] # Handles YYYY-MM-DD
            t_str = str(row['Independent Time'])
            target_ts = pd.to_datetime(f"{d_str} {t_str}")

            # Filter Logic:
            # 1. Target time is between Outage and Restore
            # 2. Meterno starts with 'SK1!'
            mask = (
                (df_melli['OutageDateTime'] <= target_ts) & 
                (df_melli['RestoreDateTime'] >= target_ts) &
                (df_melli['Meterno'].str.startswith('SK1!', na=False))
            )
            
            # Count unique consumers
            unique_consumers = df_melli[mask]['Meterno'].nunique()
            
            results.append({
                "Date": d_str,
                "Time": t_str,
                "SK1_Consumer_Count": unique_consumers
            })
            progress_bar.progress((i + 1) / total_rows)

        # Display Result Table
        st.subheader("📊 Analysis Summary")
        output_df = pd.DataFrame(results)
        st.dataframe(output_df, use_container_width=True)

        # Download Result
        csv = output_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results as CSV", csv, "outage_analysis.csv", "text/csv")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Please upload both files in the sidebar to generate the report.")
