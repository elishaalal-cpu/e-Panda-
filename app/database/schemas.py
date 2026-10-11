"""
===============================================================================
e-Panda Backend Engine: Pydantic Data Validation Schemas
===============================================================================
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class FarmerRegisterSchema(BaseModel):
    full_name: str = Field(..., example="Mary Wanjiku")
    phone_number: str = Field(..., example="+254712345678")
    email: Optional[EmailStr] = Field(None, example="mary@wanjikufarms.co.ke")
    county_location: str = Field("Kiambu", example="Kiambu")
    crop_type: str = Field("AVOCADO", example="AVOCADO")
    farm_size_acres: float = Field(1.5, example=1.5)
    preferred_language: str = Field("SW", example="SW")


class CalculationRequestSchema(BaseModel):
    latitude: float = Field(-1.03326, example=-1.03326)
    longitude: float = Field(37.06933, example=37.06933)
    crop_type: str = Field("AVOCADO", example="AVOCADO")
    growth_stage: str = Field("mid_season", example="mid_season")
    soil_type: str = Field("LOAM", example="LOAM")
    temp_c: float = Field(26.5, example=26.5)
    cloud_cover_fraction: float = Field(0.15, example=0.15)
    operating_mode: str = Field("GROWTH", example="GROWTH")
    farm_acres: float = Field(2.0, example=2.0)
