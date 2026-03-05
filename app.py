import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Power Outage Analysis", layout="wide")

st.title("⚡ Power Outage Consumer Tracker")
st.markdown("""
Upload your **Independent Time** file and the **Power outage Melli** file to calculate the number of consumers affected during specific windows.
""")

# File uploaders
col1, col2 = st.columns(2)
with col1:
    time_file = st.file_uploader("Upload Independent Time (CSV/XLSX)", type=["csv", "xlsx"])
with col2:
    melli_file = st.file_uploader("Upload Power outage Melli (XLSX)", type=["xlsx"])

if time_file and melli_file:
    try:
        # Load Independent Time Data
        if time_file.name.endswith('.csv'):
            df_ind = pd.read_csv(time_file)
        else:
            df_ind = pd.read_excel(time_file)
            
        # Load January Sheet from Melli File
        df_melli = pd.read_excel(melli_file, sheet_name="January")
        
        # Data Cleaning: Convert to Datetime
        # Assuming Melli has 'OutageDateTime' and 'RestoreDateTime'
        df_melli['OutageDateTime'] = pd.to_datetime(df_melli['OutageDateTime'])
        
        st.subheader("Analysis Results")
        
        results = []
        
        for index, row in df_ind.iterrows():
            target_date = pd.to_datetime(row['Date']).date()
            target_time_str = str(row['Independent Time'])
            
            # Create a full timestamp for the Independent Time
            target_ts = pd.to_datetime(f"{target_date} {target_time_str}")
            
            # Filter Melli data for that specific day and if the Independent Time 
            # falls within an outage period (Outage <= Target <= Restore)
            mask = (
                (df_melli['OutageDateTime'].dt.date == target_date) &
                (df_melli['OutageDateTime'] <= target_ts) &
                (df_melli['RestoreDateTime'] >= target_ts) &
                (df_melli['Meterno'].str.startswith('SK1!', na=False))
            )
            
            affected_consumers = df_melli[mask]['Meterno'].nunique()
            
            results.append({
                "Date": target_date,
                "Ref Time": target_time_str,
                "Consumers (SK1!)": affected_consumers
            })
            
        # Display results
        res_df = pd.DataFrame(results)
        st.dataframe(res_df, use_container_width=True)
        
        # Download button
        csv = res_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Report", csv, "outage_report.csv", "text/csv")

    except Exception as e:
        st.error(f"Error processing files: {e}")
        st.info("Ensure the column names 'Date', 'Independent Time', 'OutageDateTime', and 'Meterno' exist.")
