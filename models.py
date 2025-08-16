from pydantic import BaseModel, Field
from typing import Optional

class AircraftData(BaseModel):
    Date_advertisement_was_posted: Optional[str] = Field(default=None)
    Manufacture_Year_of_plane: Optional[int] = None
    Registration_number_of_plane: Optional[str] = None
    TTAF: Optional[int] = None
    Position_of_engine: Optional[str] = None
    TSN: Optional[int] = None
    CSN: Optional[int] = None
    Total_Time_Since_OH_TSOH: Optional[int] = Field(default=None, alias="Total Time Since Overhaul (TSOH)")
    Early_TBO: Optional[int] = Field(default=None, alias="Time Before Overhaul provided in the information (Early TBO)")
    HSI_Hours: Optional[int] = Field(default=None, alias="Hours since HSI (Hot Service Inspection)")
    HSI_Date: Optional[str] = Field(default=None, alias="Date of Last HSI (Hot Service Inspection)")
    Engine_Insurance_Program: Optional[str] = Field(default=None, alias="Insurance Maintenance Program the engine is enrolled in")
    Last_Overhaul_Date: Optional[str] = Field(default=None, alias="Date of Last Overhaul")
    Overhaul_Due_Date: Optional[str] = Field(default=None, alias="Date of Overhaul Due")