import streamlit as st
import pandas as pd

st.set_page_config(page_title="Power Outage Analysis", layout="wide")

st.title("⚡ SK1 Consumer Verification")

with st.sidebar:
    st.header("Upload Files")
    time_file = st.file_uploader("Independent Time File", type=['csv', 'xlsx'])
    melli_file = st.file_uploader("Power outage Melli File", type=['csv', 'xlsx'])

if time_file and melli_file:
    try:
        # Load Files
        df_ind = pd.read_csv(time_file) if time_file.name.endswith('.csv') else pd.read_excel(time_file)
        
        # Explicitly load January sheet
        if melli_file.name.endswith('.xlsx'):
            df_melli = pd.read_excel(melli_file, sheet_name='January')
        else:
            df_melli = pd.read_csv(melli_file)

        # Pre-process Melli Data
        df_melli['Meterno'] = df_melli['Meterno'].astype(str).str.strip()
        df_melli['OutageDateTime'] = pd.to_datetime(df_melli['OutageDateTime'])
        df_melli['RestoreDateTime'] = pd.to_datetime(df_melli['RestoreDateTime'])
        
        # Pre-filter for SK1
        df_sk1 = df_melli[df_melli['Meterno'].str.startswith('SK1', na=False)].copy()

        results = []

        for _, row in df_ind.iterrows():
            # Get specific Date and Time from reference
            # We use .split()[0] to ensure we only get YYYY-MM-DD
            d_ref = str(row['Date']).split(' ')[0]
            t_ref = str(row['Independent Time'])
            
            # Combine to a single timestamp
            target_ts = pd.to_datetime(f"{d_ref} {t_ref}")

            # FILTER LOGIC:
            # The outage must have STARTED before or at 8:53
            # AND it must have ENDED after or at 8:53
            mask = (df_sk1['OutageDateTime'] <= target_ts) & (df_sk1['RestoreDateTime'] >= target_ts)
            
            matches = df_sk1[mask]['Meterno'].unique().tolist()
            
            results.append({
                "Target Date": d_ref,
                "Target Time": t_ref,
                "SK1 Count": len(matches),
                "Consumer List": ", ".join(matches)
            })

        output_df = pd.DataFrame(results)
        
        st.subheader("Results")
        st.dataframe(output_df)

        # DEBUG SECTION - Manual Verification Helper
        st.divider()
        st.subheader("🔍 Verification Check")
        test_date = st.selectbox("Select Date to inspect raw SK1 data", output_df['Target Date'].unique())
        
        # Show all SK1 outages for that specific day so you can manually check
        raw_day_data = df_sk1[df_sk1['OutageDateTime'].dt.date == pd.to_datetime(test_date).date()]
        st.write(f"Showing all SK1 outages on {test_date}:")
        st.write(raw_day_data[['Meterno', 'OutageDateTime', 'RestoreDateTime']])

    except Exception as e:
        st.error(f"Error: {e}")
