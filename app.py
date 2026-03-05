import streamlit as st
import pandas as pd

st.set_page_config(page_title="Power Outage Tracker", layout="wide")

st.title("⚡ SK1 Consumer Outage Tracker")
st.markdown("""
This app matches outages based on **Date**, **Time**, and **Exact Outage Duration**. 
It only searches for consumers starting with **SK1** in the **January** sheet.
""")

# File uploaders
with st.sidebar:
    st.header("Upload Files")
    time_file = st.file_uploader("Upload Independent Time File", type=['csv', 'xlsx'])
    melli_file = st.file_uploader("Upload Power outage Melli File", type=['xlsx'])

if time_file and melli_file:
    try:
        # 1. Load Independent Time File
        if time_file.name.endswith('.csv'):
            df_ind = pd.read_csv(time_file)
        else:
            df_ind = pd.read_excel(time_file)
            
        # 2. Load Power outage Melli (January Sheet)
        df_melli = pd.read_excel(melli_file, sheet_name='January')

        # Clean Melli Column Names (removes trailing spaces)
        df_melli.columns = df_melli.columns.str.strip()
        df_ind.columns = df_ind.columns.str.strip()

        # Pre-process Melli Data
        df_melli['Meterno'] = df_melli['Meterno'].astype(str).str.strip()
        df_melli['OutageDateTime'] = pd.to_datetime(df_melli['OutageDateTime'])
        df_melli['RestoreDateTime'] = pd.to_datetime(df_melli['RestoreDateTime'])
        # Ensure Duration is numeric
        df_melli['OutageDuration'] = pd.to_numeric(df_melli['OutageDuration'], errors='coerce')
        
        # Filter globally for SK1 consumers to ensure accuracy
        df_sk1 = df_melli[df_melli['Meterno'].str.startswith('SK1', na=False)].copy()

        results = []

        # 3. Match each reference row
        for _, row in df_ind.iterrows():
            d_ref = str(row['Date']).split(' ')[0]
            t_ref = str(row['Independent Time']).strip()
            duration_ref = row['Outage Duration']
            
            # Combine Date and Time for interval checking
            try:
                target_ts = pd.to_datetime(f"{d_ref} {t_ref}")
            except:
                continue

            # NEW MATCHING LOGIC:
            # - Time must fall between Outage Start and End
            # - Outage Duration must match exactly
            mask = (
                (df_sk1['OutageDateTime'] <= target_ts) & 
                (df_sk1['RestoreDateTime'] >= target_ts) &
                (df_sk1['OutageDuration'] == duration_ref)
            )
            
            affected_meters = df_sk1[mask]['Meterno'].unique().tolist()
            
            results.append({
                "Date": d_ref,
                "Independent Time": t_ref,
                "Target Duration": duration_ref,
                "SK1 Consumer Count": len(affected_meters),
                "Consumer List": ", ".join(affected_meters) if affected_meters else "None"
            })

        # 4. Display results
        output_df = pd.DataFrame(results)
        st.subheader("📊 Analysis Results")
        st.dataframe(output_df, use_container_width=True)

        # Download button
        csv = output_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results as CSV", csv, "sk1_outage_report.csv", "text/csv")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Ensure the January sheet contains columns: Meterno, OutageDateTime, RestoreDateTime, OutageDuration")
else:
    st.info("Please upload both files in the sidebar.")
