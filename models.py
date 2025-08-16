# models.py
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class AircraftData(BaseModel):
    Date_advertisement_was_posted: Optional[str] = Field(
        default=None,
        alias="Date advertisement was posted"
    )
    Manufacture_Year_of_plane: Optional[int] = Field(
        default=None,
        alias="Manufacture Year of plane"
    )
    Registration_number_of_plane: Optional[str] = Field(
        default=None,
        alias="Registration number of plane"
    )
    TTAF: Optional[int] = Field(
        default=None,
        alias="TTAF"
    )
    Position_of_engine: Optional[List[str]] = Field(
        default=None,
        alias="Position of engine",
        description="e.g., ['Left', 'Right']"
    )
    TSN: Optional[Union[int, Dict[str, int]]] = Field(
        default=None,
        alias="TSN"
    )
    CSN: Optional[Union[int, Dict[str, int]]] = Field(
        default=None,
        alias="CSN"
    )
    Total_Time_Since_OH_TSOH: Optional[Union[int, Dict[str, int]]] = Field(
        default=None,
        alias="Total Time Since Overhaul (TSOH)"
    )
    Early_TBO: Optional[Union[int, Dict[str, int]]] = Field(
        default=None,
        alias="Time Before Overhaul provided in the information (Early TBO)"
    )
    HSI_Hours: Optional[Union[int, Dict[str, int]]] = Field(
        default=None,
        alias="Hours since HSI (Hot Service Inspection)"
    )
    HSI_Date: Optional[Union[str, Dict[str, str]]] = Field(
        default=None,
        alias="Date of Last HSI (Hot Service Inspection)"
    )
    Engine_Insurance_Program: Optional[str] = Field(
        default=None,
        alias="Insurance Maintenance Program the engine is enrolled in"
    )
    Last_Overhaul_Date: Optional[Union[str, Dict[str, str]]] = Field(
        default=None,
        alias="Date of Last Overhaul"
    )
    Overhaul_Due_Date: Optional[Union[str, Dict[str, str]]] = Field(
        default=None,
        alias="Date of Overhaul Due"
    )

    class Config:
        # Allow population by field name *and* by alias
        allow_population_by_field_name = True
        # Prevent extra fields from breaking validation
        extra = 'ignore'

    def dict(self, *args, **kwargs):
        # Ensure alias is used when converting to dict
        kwargs.setdefault('by_alias', True)
        return super().dict(*args, **kwargs)

    def model_dump(self, *args, **kwargs):
        # Modern Pydantic v2 method: ensure by_alias=True by default
        kwargs.setdefault('by_alias', True)
        return super().model_dump(*args, **kwargs)