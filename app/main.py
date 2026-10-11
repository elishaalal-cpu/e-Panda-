"""
===============================================================================
e-Panda Backend Engine: REST API & Server Entry Point
Author: Elisha Ochieng' Alal (IAAC 2026 Pre-Finalist)
Description: Connects the HTML Canvas / JS frontend directly to the Python 
             Astrophysical Core, Agronomic Engine, and FinTech Ledger.
===============================================================================
"""

from fastapi import FastAPI, Form, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.core.astrophysics import AstrophysicalEngine
from app.core.agronomics import AgronomicEngine
from app.core.fintech import ClimateFintechEngine
from app.services.ussd_sms import USSDSMSGateway
from app.database.schemas import FarmerRegisterSchema, CalculationRequestSchema

# Initialize FastAPI Application
app = FastAPI(
    title="e-Panda Precision AgTech Engine",
    description="Astrophysical Precision Agriculture & Climate-Fintech Platform for East Africa",
    version="2.0.0",
    contact={
        "name": "Elisha Ochieng' Alal",
        "organization": "UEFI Global / M-Pesa Foundation Academy Alumni",
        "email": "elisha@e-panda.co.ke",
    },
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permits requests from HTML frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root_status():
    """Health check endpoint."""
    return {
        "status": "ONLINE",
        "platform": "e-Panda Astrophysical Engine",
        "version": "2.0.0",
        "author": "Elisha Ochieng' Alal (IAAC 2026)",
        "server_time": datetime.now().isoformat(),
    }


@app.post("/api/v1/calculate-solar-irrigation")
def calculate_solar_irrigation(payload: CalculationRequestSchema):
    """
    Main API endpoint called by HTML/JS frontend.
    Computes solar irradiance, FAO-56 ETo, exact water requirements, 
    carbon credit valuation, and parametric insurance status.
    """
    day_of_year = datetime.now().timetuple().tm_yday

    # 1. Astrophysics Calculation
    astro_engine = AstrophysicalEngine(latitude=payload.latitude, longitude=payload.longitude)
    solar_data = astro_engine.calculate_effective_ground_irradiance(
        day_of_year=day_of_year, cloud_cover_fraction=payload.cloud_cover_fraction
    )

    # 2. Agronomic Calculation
    water_data = AgronomicEngine.calculate_crop_water_requirement(
        solar_radiation_MJ_m2=solar_data["daily_solar_radiation_MJ_m2"],
        crop_type=payload.crop_type,
        growth_stage=payload.growth_stage,
        soil_type=payload.soil_type,
        temp_c=payload.temp_c,
        operating_mode=payload.operating_mode,
    )

    # 3. FinTech Calculation
    carbon_data = ClimateFintechEngine.calculate_biomass_and_carbon_credit(
        crop_type=payload.crop_type,
        daily_solar_radiation_MJ_m2=solar_data["daily_solar_radiation_MJ_m2"],
        farm_acres=payload.farm_acres,
    )

    insurance_data = ClimateFintechEngine.evaluate_parametric_insurance_trigger(
        consecutive_dry_days=8,
        mean_solar_irradiance_W_m2=solar_data["I_effective_W_m2"],
        rainfall_7_days_mm=0.0,
    )

    export_token = ClimateFintechEngine.generate_export_traceability_token(
        farmer_id="EP-8842",
        farm_location="Thika, Kiambu",
        water_saved_liters=water_data["liters_per_plant_day"] * 0.40,
    )

    return {
        "success": True,
        "astrophysics": solar_data,
        "agronomics": water_data,
        "carbon_ledger": carbon_data,
        "parametric_insurance": insurance_data,
        "export_traceability": export_token,
    }


@app.post("/api/v1/register-farmer")
def register_farmer(farmer: FarmerRegisterSchema):
    """Registers new farmer and generates confirmation payload."""
    return {
        "status": "SUCCESS",
        "message_en": f"Welcome {farmer.full_name}! Your farm ({farmer.crop_type}, {farmer.farm_size_acres} acres) is registered on e-Panda.",
        "message_sw": f"Karibu {farmer.full_name}! Shamba lako ({farmer.crop_type}, ekari {farmer.farm_size_acres}) limesajiliwa e-Panda.",
        "account_id": "EP-KENYA-2026-9912",
        "ussd_shortcode": "*384*#",
    }


@app.post("/ussd")
def ussd_callback(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(...),
):
    """USSD Callback route for Africa's Talking API."""
    response_text = USSDSMSGateway.handle_ussd_request(
        session_id=sessionId, service_code=serviceCode, phone_number=phoneNumber, text=text
    )
    return Response(content=response_text, media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    # Run server locally on http://localhost:8000
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
