import streamlit as st
import pandas as pd

st.set_page_config(page_title="SK1 Outage Analysis", layout="wide")

st.title("⚡ SK1 Consumer Outage Tracker")
st.markdown("""
This tool finds **SK1 consumers** where the target time falls exactly within their outage window 
**AND** their outage duration matches the reference file exactly.
""")

with st.sidebar:
    st.header("Upload Data")
    time_file = st.file_uploader("Upload Independent Time File", type=['csv', 'xlsx'])
    melli_file = st.file_uploader("Upload Power outage Melli File (January Sheet)", type=['csv', 'xlsx'])

if time_file and melli_file:
    try:
        # 1. Load Independent Time File
        if time_file.name.endswith('.csv'):
            df_ind = pd.read_csv(time_file)
        else:
            df_ind = pd.read_excel(time_file)
        
        # Forward fill the Date column (crucial if date is only in the first row)
        df_ind['Date'] = df_ind['Date'].ffill()

        # 2. Load Power outage Melli (January Sheet)
        if melli_file.name.endswith('.xlsx'):
            df_melli = pd.read_excel(melli_file, sheet_name='January')
        else:
            df_melli = pd.read_csv(melli_file)

        # 3. Clean and Standardize Data
        df_melli.columns = df_melli.columns.str.strip()
        df_melli['Meterno'] = df_melli['Meterno'].astype(str).str.strip()
        df_melli['OutageDateTime'] = pd.to_datetime(df_melli['OutageDateTime'], errors='coerce')
        df_melli['RestoreDateTime'] = pd.to_datetime(df_melli['RestoreDateTime'], errors='coerce')
        df_melli['OutageDuration'] = pd.to_numeric(df_melli['OutageDuration'], errors='coerce')
        
        # Pre-filter for SK1
        df_sk1 = df_melli[df_melli['Meterno'].str.startswith('SK1', na=False)].dropna(subset=['OutageDateTime', 'RestoreDateTime']).copy()

        results = []

        # 4. Processing logic
        for _, row in df_ind.iterrows():
            d_ref = str(row['Date']).split(' ')[0]
            t_ref = str(row['Independent Time']).strip()
            dur_ref = row['Outage Duration']
            
            # Combine Date and Time for matching
            try:
                target_ts = pd.to_datetime(f"{d_ref} {t_ref}")
            except:
                continue

            # MATCHING CONDITIONS:
            # - Meterno starts with SK1 (already filtered in df_sk1)
            # - OutageDuration matches exactly (e.g., 2 == 2)
            # - target_ts falls between Outage and Restore times
            mask = (
                (df_sk1['OutageDuration'] == dur_ref) &
                (df_sk1['OutageDateTime'] <= target_ts) &
                (df_sk1['RestoreDateTime'] >= target_ts)
            )
            
            # Group by Meterno to get unique consumers
            affected = df_sk1[mask]['Meterno'].unique().tolist()
            
            results.append({
                "Reference Date": d_ref,
                "Reference Time": t_ref,
                "Target Duration": dur_ref,
                "SK1 Count": len(affected),
                "SK1 Consumer List": ", ".join(affected) if affected else "None"
            })

        # 5. Output results
        output_df = pd.DataFrame(results)
        st.subheader("📊 Matching Results")
        st.dataframe(output_df, use_container_width=True)

        # Download button
        csv = output_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Analysis CSV", csv, "sk1_outage_analysis.csv", "text/csv")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload both files to generate the precise report.")
