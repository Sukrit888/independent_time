import streamlit as st
import pandas as pd

st.set_page_config(page_title="Power Outage Analysis", layout="wide")

st.title("⚡ SK1 Consumer Tracker")

with st.sidebar:
    st.header("Upload Files")
    time_file = st.file_uploader("Independent Time File", type=['csv', 'xlsx'])
    melli_file = st.file_uploader("Power outage Melli (January Sheet)", type=['csv', 'xlsx'])

if time_file and melli_file:
    try:
        # Load Files
        df_ind = pd.read_csv(time_file) if time_file.name.endswith('.csv') else pd.read_excel(time_file)
        df_melli = pd.read_excel(melli_file, sheet_name='January') if melli_file.name.endswith('.xlsx') else pd.read_csv(melli_file)

        # Clean Data
        df_melli['Meterno'] = df_melli['Meterno'].astype(str).str.strip()
        df_melli['OutageDateTime'] = pd.to_datetime(df_melli['OutageDateTime'])
        df_melli['RestoreDateTime'] = pd.to_datetime(df_melli['RestoreDateTime'])
        
        results = []

        for _, row in df_ind.iterrows():
            d_ref = str(row['Date']).split(' ')[0]
            t_ref = str(row['Independent Time']) # e.g., "8:53"
            
            # Create comparison objects using exact hour/minute
            # This ignores seconds entirely
            target_dt = pd.to_datetime(d_ref)
            
            # Logic: Check if the outage covers the specific Hour and Minute
            mask = (
                (df_melli['OutageDateTime'].dt.date == target_dt.date()) &
                (df_melli['Meterno'].str.startswith('SK1', na=False)) &
                (df_melli['OutageDateTime'].dt.strftime('%H:%M') <= t_ref) &
                (df_melli['RestoreDateTime'].dt.strftime('%H:%M') >= t_ref)
            )
            
            matches = df_melli[mask]['Meterno'].unique().tolist()
            
            results.append({
                "Date": d_ref,
                "Time": t_ref,
                "SK1 Count": len(matches),
                "Consumer List": ", ".join(matches) if matches else "None"
            })

        output_df = pd.DataFrame(results)
        st.dataframe(output_df, use_container_width=True)
        
        st.download_button("Download CSV", output_df.to_csv(index=False), "results.csv")

    except Exception as e:
        st.error(f"Error: {e}")
