import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

# Import your custom module
from extractor import AircraftDataExtractor

# === Page Configuration ===
st.set_page_config(
    page_title="Aircraft Data Extractor",
    page_icon="✈️",
    layout="wide"
)

# === Custom CSS for Better Styling ===
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #007BFF;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .reportview-container .markdown-text-container {
        font-family: monospace;
    }
    .stJson {
        border: 1px solid #d1d7e0;
        border-radius: 8px;
        padding: 10px;
        background-color: #f1f3f5;
    }
    .stProgress > div > div > div > div {
        background-color: #007BFF;
    }
    .title {
        text-align: center;
        color: #007BFF;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 18px;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# === Header ===
st.markdown('<p class="title">Aircraft Data Extraction Tool</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Extract structured data from aircraft listings using AI </p>', unsafe_allow_html=True)

# === Load API Key ===
@st.cache_resource
def load_api_key():
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        load_dotenv()
        return os.getenv("OPENROUTER_API_KEY")

api_key = load_api_key()

if not api_key:
    st.error("❌ `OPENROUTER_API_KEY` not found. Please set it in `.env` or Streamlit secrets.")
    st.info("💡 Create a `.env` file with: `OPENROUTER_API_KEY=your_key_here`")
    st.stop()

# === Initialize Extractor ===
@st.cache_resource
def get_extractor():
    return AircraftDataExtractor(api_key)

extractor = get_extractor()

# === Tabs ===
tab1, tab2 = st.tabs(["📝 Single Text Input", "📂 Upload Excel File"])

# === Tab 1: Single Input ===
with tab1:
    st.subheader("Enter Aircraft Listing Text")
    st.write("Paste the full aircraft ad below for structured data extraction.")

    user_input = st.text_area(
        "Aircraft Description",
        height=200,
        placeholder="E.g., 2018 Cessna 172 Skyhawk, 1,200 TTAF, Garmin G1000, located in Florida...",
        help="The AI will extract model, year, specs, price, and more from this text."
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        submit_single = st.button("🔍 Extract Data", key="single")

    if submit_single:
        if not user_input.strip():
            st.warning("⚠️ Please enter some text before extracting.")
        else:
            with st.spinner("🧠 Analyzing text with AI..."):
                result = extractor.extract_single(user_input)

            if "error" in result:
                st.error(f"❌ Extraction failed: {result['error']}")
            else:
                st.success("✅ Extraction Successful!")
                with st.expander("📋 View Extracted Data", expanded=True):
                    st.json(result)

# === Tab 2: Batch Upload ===
with tab2:
    st.subheader("Upload Excel File for Batch Processing")
    st.write("Upload an Excel file with a `Description` column to extract data from all rows.")

    uploaded_file = st.file_uploader(
        "Choose an Excel file (.xlsx)",
        type=["xlsx"],
        help="File must contain a column named 'Description' with aircraft listing text."
    )

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.info(f"📄 Loaded {len(df)} rows. Columns: {list(df.columns)}")

            if "Description" not in df.columns:
                st.error("❌ Missing required column: `Description`")
                st.stop()

            non_empty_count = df["Description"].dropna().astype(str).str.strip().ne("").sum()
            st.write(f"✅ Found {int(non_empty_count)} non-empty descriptions to process.")

            if st.button("Process All Rows", key="batch"):
                results = []
                progress_bar = st.progress(0)
                status_text = st.empty()

                total_rows = len(df)
                processed = 0

                for idx, row in df.iterrows():
                    desc = str(row["Description"]).strip()
                    if not desc:
                        results.append({"error": "Empty description"})
                        continue

                    status_text.write(f"Processing row {idx + 1} of {total_rows}...")
                    result = extractor.extract_single(desc)
                    results.append(result)
                    processed += 1
                    progress_bar.progress(processed / total_rows)

                status_text.write("✅ Batch processing complete!")
                result_df = pd.DataFrame(results)

                # Display results
                st.markdown("### 📊 Extraction Results")
                st.dataframe(result_df, use_container_width=True)

                # Download CSV
                csv = result_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name="aircraft_extraction_results.csv",
                    mime="text/csv",
                    help="Click to download the structured data as a CSV file."
                )

        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")