import streamlit as st
import pandas as pd

st.set_page_config(page_title="Power Outage Analysis", layout="wide")

st.title("⚡ SK1 Consumer Outage Tracker")

# Sidebar for file uploads
with st.sidebar:
    st.header("Upload Files")
    time_file = st.file_uploader("Upload Independent Time File", type=['csv', 'xlsx'])
    melli_file = st.file_uploader("Upload Power outage Melli File", type=['csv', 'xlsx'])

if time_file and melli_file:
    try:
        # Load Reference Times
        df_ind = pd.read_csv(time_file) if time_file.name.endswith('.csv') else pd.read_excel(time_file)
        
        # Load Melli January Data
        if melli_file.name.endswith('.xlsx'):
            # Explicitly load the January sheet as requested
            df_melli = pd.read_excel(melli_file, sheet_name='January')
        else:
            df_melli = pd.read_csv(melli_file)

        # --- DATA CLEANING ---
        # Ensure Meterno is string and strip spaces
        df_melli['Meterno'] = df_melli['Meterno'].astype(str).str.strip()
        
        # Convert Outage/Restore columns to datetime
        df_melli['OutageDateTime'] = pd.to_datetime(df_melli['OutageDateTime'])
        df_melli['RestoreDateTime'] = pd.to_datetime(df_melli['RestoreDateTime'])
        
        # Filter for ONLY SK1 consumers globally to speed up the app
        df_sk1 = df_melli[df_melli['Meterno'].str.startswith('SK1', na=False)].copy()

        results = []

        # --- PROCESSING ---
        for _, row in df_ind.iterrows():
            # Standardize Date and Time from Reference File
            ref_date = str(row['Date']).split(' ')[0]
            ref_time = str(row['Independent Time'])
            
            # Create a combined timestamp for the target
            target_ts = pd.to_datetime(f"{ref_date} {ref_time}")

            # LOGIC: Does target_ts fall WITHIN the outage window?
            # (OutageDateTime <= Target <= RestoreDateTime)
            mask = (df_sk1['OutageDateTime'] <= target_ts) & (df_sk1['RestoreDateTime'] >= target_ts)
            
            # Find all unique meters starting with SK1 during this window
            affected_meters = df_sk1[mask]['Meterno'].unique().tolist()
            
            results.append({
                "Reference Date": ref_date,
                "Reference Time": ref_time,
                "No. of SK1 Consumers": len(affected_meters),
                "List of Consumers": ", ".join(affected_meters)
            })

        # Display Results
        output_df = pd.DataFrame(results)
        st.subheader("📊 Analysis Results")
        
        if len(output_df) > 0 and output_df["No. of SK1 Consumers"].sum() > 0:
            st.dataframe(output_df, use_container_width=True)
            
            # Download link
            csv = output_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Result CSV", csv, "outage_report.csv", "text/csv")
        else:
            st.error("No SK1 consumers found for these times. Check if the 'Meterno' column starts with 'SK1' exactly (no symbols like '!' unless specified).")
            st.info("Debugging: Showing first few rows of your Melli data below:")
            st.write(df_melli.head())

    except Exception as e:
        st.error(f"Error processing files: {e}")
else:
    st.info("Please upload both files to start.")
