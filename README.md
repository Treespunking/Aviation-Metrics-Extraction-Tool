# Aviation Aircraft Data Extractor

A smart data extraction tool to parse aircraft listing information and extract structured technical and maintenance data using **LLM-powered parsing** with validation and intelligent field calculation.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![LangChain](https://img.shields.io/badge/Tool-LangChain-purple)
![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-orange)

---

## Features
- Extracts key aircraft engine and maintenance data from unstructured text
- Powered by **Qwen3-235B** via OpenRouter for high-accuracy parsing
- Handles multi-engine configurations (e.g., Left/Right values)
- Validates output using Pydantic models
- Calculates derived fields (e.g., time remaining before overhaul)
- Supports dynamic date and numeric field resolution
- Clean, modular code with error handling and logging

---

## Requirements
- Python 3.8+
- OpenRouter API key (free tier supported)
- Internet access for LLM inference

---

## Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/Treespunking/Aviation-Metrics-Extraction-Tool.git
cd Aviation-Metrics-Extraction-Tool
```

### 2. Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> If missing, create `requirements.txt` with:
```txt
streamlit
langchain
langchain-openai
pydantic
pandas
openpyxl
python-dotenv
pytest
```

### 4. Add your API key in `.env`
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```
> Never commit this file! It should be in `.gitignore`.

### 5. Run the extraction (example)
```bash
python extractor.py
```
> Note: This is a library module. Use via script or integrate into your app.

---

## How It Works

The system uses a **prompt-engineered LLM chain** to extract structured data from aircraft listings:

1. Input text (e.g., aircraft ad) is sent to the LLM
2. Model extracts fields like TSN, CSN, TTAF, overhaul dates, etc.
3. Output is cleaned and parsed into valid JSON
4. Data is validated using Pydantic model
5. Additional fields are calculated (e.g., time remaining before overhaul)

### Calculated Fields
- `Time Remaining before Overhaul`: Based on program, HSI, TSOH, or TSN
- `Basis of Calculation`: Why the above value was chosen
- `On Condition Repair`: Flags if engine is likely on-condition
- `Average Hours left`: Estimated usage at 450 hrs/year

---

## Project Structure
```
aviation-data-extractor/
│
├── extractor.py             # Main extraction logic
├── models.py                # Pydantic data model
├── requirements.txt         # Dependencies
├── streamlit_app.py         # (Optional) Web UI for demo
```

---

## Example Usage

```python
from extractor import AircraftDataExtractor

extractor = AircraftDataExtractor(api_key="your-key")

text = """
2005 Cessna 172S, Reg: N12345, TTAF: 4850 hours. 
Engine: Lycoming IO-360-L2A, TSN: 1200 (both engines), CSN: 890. 
Last HSI: 2023-05-15, 3200 hours since HSI. Enrolled in Lycoming ESP.
"""

result = extractor.extract_single(text)
print(result)
```

---

## Output Example
```json
{
  "Date advertisement was posted": null,
  "Manufacture Year of plane": 2005,
  "Registration number of plane": "N12345",
  "TTAF": 4850,
  "Position of engine": ["Left", "Right"],
  "TSN": 1200,
  "CSN": 890,
  "Total Time Since Overhaul (TSOH)": null,
  "Time Before Overhaul provided in the information (Early TBO)": null,
  "Hours since HSI (Hot Service Inspection)": 3200,
  "Date of Last HSI (Hot Service Inspection)": "2023-05-15",
  "Insurance Maintenance Program the engine is enrolled in": "Lycoming ESP",
  "Date of Last Overhaul": null,
  "Date of Overhaul Due": null,
  "Engine Maintenance Insurance Program Name": "Lycoming ESP",
  "Time Remaining before Overhaul": 8000,
  "Basis of Calculation": "Insurance Maintenance Program",
  "years left for operation": null,
  "Average Hours left for operation according to 450 hours annual usage": null,
  "On Condition Repair": false
}
```

---
