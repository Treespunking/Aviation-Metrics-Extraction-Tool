### **Project Overview: Aircraft Data Extraction Tool**

---

#### **Problem Statement**

In the aviation industry, aircraft listings—whether from brokers, marketplaces, or internal databases—are typically published as unstructured text. These descriptions contain critical technical and operational data such as engine hours, overhaul history, registration numbers, and maintenance programs. However, manually extracting and structuring this information is time-consuming, error-prone, and inefficient, especially when processing large volumes of listings.

This lack of automation hinders key workflows including aircraft valuation, compliance tracking, pre-purchase evaluations, and fleet management. Without a standardized way to convert free-form text into structured, analyzable data, organizations face delays and inconsistencies in decision-making.

---

#### **Approach**

To address this challenge, we developed an AI-powered **Aircraft Data Extraction Tool** that automatically parses unstructured aircraft listings and extracts specific, high-value fields into a consistent JSON format. The solution leverages the following components:

- **Large Language Model (LLM)**: Utilizing Qwen3 via OpenRouter, the system understands natural language descriptions and identifies relevant aircraft data with high accuracy.
- **Structured Prompt Engineering**: A carefully designed system prompt instructs the LLM to extract only predefined fields and return clean, valid JSON—without explanations, formatting, or extraneous text.
- **Pydantic Data Validation**: A robust `AircraftData` model enforces schema validation, ensuring extracted values meet expected types (e.g., integers for TSN, dates for overhauls).
- **Post-Processing Logic**: Calculated fields such as *Time Remaining Before Overhaul*, *Years Left for Operation*, and *On-Condition Repair Status* are derived using business rules based on extracted values.
- **Flexible Input Handling**: The tool supports both single-text input (for quick analysis) and batch processing via Excel upload, making it suitable for individual users and enterprise use cases.
- **Streamlit Frontend**: A user-friendly web interface allows non-technical users to interact with the tool easily, view results in real-time, and export structured outputs.

The system is built using modern Python frameworks including `langchain`, `pydantic v2`, `pandas`, and `Streamlit`, ensuring scalability, maintainability, and seamless integration.

---

#### **Solution**

The **Aircraft Data Extraction Tool** transforms unstructured aircraft listings into structured, actionable data with minimal user effort. Key features include:

- **Accurate Field Extraction**: Automatically identifies and extracts 15+ critical fields such as:
  - Manufacture year
  - Registration number
  - TTAF, TSN, CSN
  - Engine position and overhaul history
  - HSI (Hot Section Inspection) details
  - Insurance maintenance program enrollment

- **Smart Data Enrichment**:
  - Calculates remaining time before overhaul based on engine program, HSI, or midlife rules.
  - Determines operational lifespan in years and estimated flight hours.
  - Flags aircraft under *on-condition* maintenance regimes.

- **Robust Error Handling**:
  - Cleans malformed LLM outputs (e.g., removes `<think>` tags, extracts embedded JSON).
  - Validates data integrity and provides clear error messages when parsing fails.

- **User-Friendly Interface**:
  - Two modes: single text input and batch Excel processing.
  - Real-time feedback with progress tracking during batch jobs.
  - Exportable CSV results for downstream analysis.

- **Deployment Ready**:
  - Secure API key management via environment variables or Streamlit secrets.
  - Modular design allows integration into larger aviation data platforms.

---
