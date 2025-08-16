import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from extractor import AircraftDataExtractor

# Page config
st.set_page_config(page_title="Aircraft Data Extractor", layout="wide")
st.title("Aircraft Data Extraction Tool")
st.markdown("Extract structured data from aircraft listings using AI.")

# Load API key
# Use Streamlit secrets in production
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    st.error("OPENROUTER_API_KEY not found in secrets or .env")
    st.stop()

if not api_key:
    st.error("OPENROUTER_API_KEY not found in `.env`. Please add it.")
    st.stop()

# Initialize extractor
@st.cache_resource
def get_extractor():
    return AircraftDataExtractor(api_key)

extractor = get_extractor()

# Tabs
tab1, tab2 = st.tabs(["📝 Single Text Input", "📂 Upload Excel File"])

# --- Tab 1: Single Input ---
with tab1:
    user_input = st.text_area("Enter Aircraft Listing:", height=200, placeholder="Paste the aircraft ad text here...")
    if st.button("Extract Data", key="single"):
        if not user_input.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Extracting..."):
                result = extractor.extract_single(user_input)
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("Extraction Successful!")
                st.json(result)

# --- Tab 2: Upload File ---
with tab2:
    uploaded_file = st.file_uploader("Upload Excel File (Test42Inputs.xlsx)", type=["xlsx"])
    if uploaded_file and st.button("Process All Rows", key="batch"):
        df = pd.read_excel(uploaded_file)
        if "Description" not in df.columns:
            st.error("Excel must have a 'Description' column.")
        else:
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, row in df.iterrows():
                desc = str(row["Description"]).strip()
                if not desc:
                    continue
                status_text.write(f"Processing row {idx + 1}...")
                result = extractor.extract_single(desc)
                results.append(result)
                progress_bar.progress((idx + 1) / len(df))

            status_text.write("✅ Processing complete!")
            result_df = pd.DataFrame(results)

            # Show preview
            st.dataframe(result_df)

            # Download CSV
            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="aircraft_extraction_results.csv",
                mime="text/csv"
            )