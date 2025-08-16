# extractor.py
import os
import re
import json
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models import AircraftData
from pydantic import ValidationError


class AircraftDataExtractor:
    def __init__(self, api_key: str):
        self.api_key = api_key

        # Initialize LLM with OpenRouter
        self.model = ChatOpenAI(
            api_key=self.api_key,
            model="qwen/qwen3-235b-a22b:free",
            base_url="https://openrouter.ai/api/v1",  # Cleaned: no trailing spaces
            default_headers={
                "HTTP-Referer": "https://your-site.com",  # Cleaned
                "X-Title": "Your Site Name"
            },
            temperature=0
        )

        # System prompt with clear instructions
        self.prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an expert aircraft data extraction assistant.
    Extract the following fields from the listing and return ONLY a valid JSON object.

    ⚠️ DO NOT include any thoughts, explanations, or reasoning.
    ⚠️ DO NOT use <think>, </think>, or any XML/HTML-like tags.
    ⚠️ DO NOT wrap the JSON in markdown (```json or ```).
    ⚠️ Start with {{ and end with }}.

    If the aircraft has multiple engines, format engine-specific values as objects. Example:
    {{
      "TSN": {{"Left": 12345, "Right": 12346}},
      "Position of engine": ["Left", "Right"]
    }}
    But if values are the same or not separated, you may return a single value.

    Fields to extract:
    - Date advertisement was posted
    - Manufacture Year of plane
    - Registration number of plane
    - TTAF
    - Position of engine
    - TSN
    - CSN
    - Total Time Since Overhaul (TSOH)
    - Time Before Overhaul provided in the information (Early TBO)
    - Hours since HSI (Hot Service Inspection)
    - Date of Last HSI (Hot Service Inspection)
    - Insurance Maintenance Program the engine is enrolled in
    - Date of Last Overhaul
    - Date of Overhaul Due

    If a field is missing, use null.
    Return ONLY the JSON. No prefixes, no suffixes, no comments.
    """),
    ("user", "{text}")
])

        # Build chain
        self.chain = self.prompt | self.model | StrOutputParser()

    def extract_single(self, text: str):
        try:
            response = self.chain.invoke({"text": text})
            
            # Clean the response: remove <think> blocks and markdown
            cleaned_response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
            cleaned_response = re.sub(r"```json|```", "", cleaned_response).strip()
            cleaned_response = cleaned_response.strip()

            # Try parsing JSON
            try:
                data_dict = json.loads(cleaned_response)
            except json.JSONDecodeError:
                # Fallback: extract first JSON object with regex
                json_match = re.search(r"\{.*\}", cleaned_response, re.DOTALL)
                if not json_match:
                    return {"error": f"No JSON object found in response: {cleaned_response}"}
                data_dict = json.loads(json_match.group())

            # Validate using Pydantic model
            data = AircraftData.model_validate(data_dict)
            raw_dict = data.model_dump(by_alias=True)  # Keep original field names
            return self._calculate_fields(raw_dict)

        except json.JSONDecodeError as je:
            return {"error": f"JSON decode failed after cleaning: {str(je)}\nCleaned response: {cleaned_response}"}
        except ValidationError as ve:
            return {"error": f"Validation failed: {ve}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def _safe_int_from_dynamic(self, val):
        """Handle int, {'Left': n, 'Right': n} → return max value"""
        if val is None:
            return None
        if isinstance(val, int):
            return val
        if isinstance(val, dict):
            values = [v for v in val.values() if isinstance(v, (int, float))]
            return max(values) if values else None
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    def _get_date_from_dynamic(self, val):
        """Extract date string from str or dict"""
        if isinstance(val, str):
            return val
        if isinstance(val, dict):
            # Return first valid date string from dict values
            for v in val.values():
                if isinstance(v, str):
                    return v
        return None

    def _safe_int(self, val):
        """Legacy helper (kept for clarity)"""
        return self._safe_int_from_dynamic(val)

    def _safe_date(self, val):
        """Parse date string to datetime object"""
        try:
            return datetime.strptime(str(val).strip(), "%Y-%m-%d")
        except Exception:
            return None

    def _calculate_fields(self, data: dict):
        # Extract scalar values from potentially structured input
        tsn = self._safe_int_from_dynamic(data.get("TSN"))
        tsOh = self._safe_int_from_dynamic(data.get("Total Time Since Overhaul (TSOH)"))
        hsi_hours = self._safe_int_from_dynamic(data.get("Hours since HSI (Hot Service Inspection)"))
        engine_program = data.get("Insurance Maintenance Program the engine is enrolled in")

        basis_of_calculation = None
        time_remaining_before_overhaul = None

        if engine_program:
            time_remaining_before_overhaul = 8000
            basis_of_calculation = "Insurance Maintenance Program"
        elif hsi_hours is not None:
            time_remaining_before_overhaul = max(0, 4000 - hsi_hours)
            basis_of_calculation = "Midlife Calculation"
        elif tsOh is not None:
            time_remaining_before_overhaul = max(0, 4000 - tsOh)
            basis_of_calculation = "Midlife Calculation"
        elif tsn is not None:
            if tsn < 8000:
                time_remaining_before_overhaul = 8000 - tsn
                basis_of_calculation = "time since new"
            else:
                time_remaining_before_overhaul = 0
                basis_of_calculation = "condition based"

        # Parse dates (support both string and dict)
        date_ad_posted = self._safe_date(data.get("Date advertisement was posted"))
        date_last_overhaul = self._safe_date(self._get_date_from_dynamic(data.get("Date of Last Overhaul")))
        date_overhaul_due = self._safe_date(self._get_date_from_dynamic(data.get("Date of Overhaul Due")))

        years_left_for_operation = None
        if date_overhaul_due and date_ad_posted:
            years_left_for_operation = round((date_overhaul_due - date_ad_posted).days / 365, 2)
        elif date_last_overhaul and date_ad_posted:
            years_left_for_operation = round((date_ad_posted - date_last_overhaul).days / 365, 2)

        avg_hours_left = None
        if years_left_for_operation is not None:
            avg_hours_left = round(years_left_for_operation * 450, 2)

        on_condition_repair = False
        if (
            tsn is not None and tsn > 8000 and
            tsOh is None and
            hsi_hours is None and
            data.get("Date of Last HSI (Hot Service Inspection)") is None and
            date_last_overhaul is None
        ):
            on_condition_repair = True

        # Build final output with consistent keys
        cleaned = {k: data.get(k) for k in [
            "Date advertisement was posted",
            "Manufacture Year of plane",
            "Registration number of plane",
            "TTAF",
            "Position of engine",
            "Total Time Since Overhaul (TSOH)",
            "Time Before Overhaul provided in the information (Early TBO)",
            "Hours since HSI (Hot Service Inspection)",
            "Date of Last HSI (Hot Service Inspection)",
            "Date of Overhaul Due",
            "Date of Last Overhaul",
        ]}

        # Add renamed and calculated fields
        cleaned["Engine Maintenance Insurance Program Name"] = engine_program
        cleaned["TSN"] = tsn
        cleaned["CSN"] = self._safe_int_from_dynamic(data.get("CSN"))

        cleaned["Time Remaining before Overhaul"] = time_remaining_before_overhaul
        cleaned["Basis of Calculation"] = basis_of_calculation
        cleaned["years left for operation"] = years_left_for_operation
        cleaned["Average Hours left for operation according to 450 hours annual usage"] = avg_hours_left
        cleaned["On Condition Repair"] = on_condition_repair

        return cleaned