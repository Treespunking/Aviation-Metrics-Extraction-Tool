import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models import AircraftData
from pydantic import ValidationError

class AircraftDataExtractor:
    def __init__(self, api_key):
        self.api_key = api_key

        self.model = ChatOpenAI(
            api_key=self.api_key,
            model="qwen/qwen3-235b-a22b:free",
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://your-site.com",
                "X-Title": "Your Site Name"
            },
            temperature=0
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an expert aircraft data extraction assistant.
            Extract the following fields from the listing and return only valid JSON:
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

            Return ONLY the JSON object. No extra text.
            """),
            ("user", "{text}")
        ])

        self.chain = self.prompt | self.model | StrOutputParser()

    def extract_single(self, text):
        try:
            response = self.chain.invoke({"text": text})
            data = AircraftData.parse_raw(response)
            raw_dict = data.dict(by_alias=True)  # Keep original field names
            return self._calculate_fields(raw_dict)
        except ValidationError as ve:
            return {"error": f"Validation failed: {ve}"}
        except Exception as e:
            return {"error": str(e)}

    def _safe_int(self, val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    def _safe_date(self, val):
        try:
            return datetime.strptime(str(val).strip(), "%Y-%m-%d")
        except Exception:
            return None

    def _calculate_fields(self, data):
        tsn = self._safe_int(data.get("TSN"))
        tsOh = self._safe_int(data.get("Total Time Since Overhaul (TSOH)"))
        hsi_hours = self._safe_int(data.get("Hours since HSI (Hot Service Inspection)"))
        engine_program = data.get("Insurance Maintenance Program the engine is enrolled in")

        basis = "condition based"
        time_left = 0

        if engine_program:
            time_left = 8000
            basis = "Insurance Maintenance Program"
        elif hsi_hours is not None:
            time_left = max(0, 4000 - hsi_hours)
            basis = "Midlife Calculation"
        elif tsOh is not None:
            time_left = max(0, 4000 - tsOh)
            basis = "Midlife Calculation"
        elif tsn is not None and tsn < 8000:
            time_left = 8000 - tsn
            basis = "time since new"

        date_posted = self._safe_date(data.get("Date advertisement was posted"))
        last_oh = self._safe_date(data.get("Date of Last Overhaul"))
        due_oh = self._safe_date(data.get("Date of Overhaul Due"))

        years_left = None
        if due_oh and date_posted:
            years_left = round((due_oh - date_posted).days / 365, 2)
        elif last_oh and date_posted:
            years_left = round((date_posted - last_oh).days / 365, 2)

        avg_hours = round(years_left * 450, 2) if years_left else None

        on_condition = False
        if tsn and tsn > 8000 and not tsOh and not hsi_hours and not data.get("Date of Last HSI (Hot Service Inspection)") and not last_oh:
            on_condition = True

        # Final output with clean keys
        return {
            "Date advertisement was posted": data.get("Date advertisement was posted"),
            "Manufacture Year of plane": data.get("Manufacture Year of plane"),
            "Registration number of plane": data.get("Registration number of plane"),
            "TTAF": data.get("TTAF"),
            "Position of engine": data.get("Position of engine"),
            "TSN": data.get("TSN"),
            "CSN": data.get("CSN"),
            "Total Time Since Overhaul (TSOH)": data.get("Total Time Since Overhaul (TSOH)"),
            "Time Before Overhaul provided in the information (Early TBO)": data.get("Time Before Overhaul provided in the information (Early TBO)"),
            "Hours since HSI (Hot Service Inspection)": data.get("Hours since HSI (Hot Service Inspection)"),
            "Date of Last HSI (Hot Service Inspection)": data.get("Date of Last HSI (Hot Service Inspection)"),
            "Engine Maintenance Insurance Program Name": engine_program,
            "Date of Overhaul Due": data.get("Date of Overhaul Due"),
            "Date of Last Overhaul": data.get("Date of Last Overhaul"),
            "Time Remaining before Overhaul": time_left,
            "Basis of Calculation": basis,
            "years left for operation": years_left,
            "Average Hours left for operation according to 450 hours annual usage": avg_hours,
            "On Condition Repair": on_condition,
        }