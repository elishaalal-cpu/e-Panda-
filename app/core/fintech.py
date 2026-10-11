"""
===============================================================================
e-Panda Backend Engine: Climate-Fintech & Carbon Ledger Module
Author: Elisha Ochieng' Alal
Description: Converts solar irradiance data into verified Carbon Credits (RUE),
             triggers Parametric Micro-Insurance claims, and mints export QR tokens.
===============================================================================
"""

import hashlib
import time
from typing import Dict, Any


class ClimateFintechEngine:
    # Radiation Use Efficiency (RUE) Constants (g Biomass per MJ absorbed PAR)
    RUE_FACTORS: Dict[str, float] = {
        "AVOCADO": 1.65,
        "ROSE": 1.20,
        "TEA": 1.85,
        "COFFEE": 1.40,
        "MAIZE": 2.10,
    }

    # Photosynthetically Active Radiation (PAR) fraction of total solar flux
    PAR_FRACTION: float = 0.48
    CARBON_CONTENT_DRY_MATTER: float = 0.45 # ~45% of plant biomass is elemental C
    CO2_MOLECULAR_RATIO: float = 44.0 / 12.0 # CO2 weight relative to C weight

    @classmethod
    def calculate_biomass_and_carbon_credit(
        cls, crop_type: str, daily_solar_radiation_MJ_m2: float, farm_acres: float
    ) -> Dict[str, Any]:
        """
        Calculates daily accumulated biomass and CO2 sequestered using RUE equations:
        PAR = Solar_Radiation * 0.48
        Biomass (g/m^2) = PAR * RUE
        Sequestered CO2 (kg/acre) = Biomass * 0.45 * (44/12) * 4.04686
        """
        crop_key = crop_type.upper()
        rue = cls.RUE_FACTORS.get(crop_key, 1.50)

        par_energy = daily_solar_radiation_MJ_m2 * cls.PAR_FRACTION
        daily_biomass_g_m2 = par_energy * rue

        # Convert g/m^2 to kg per acre (1 acre = 4046.86 m^2)
        daily_biomass_kg_acre = (daily_biomass_g_m2 / 1000.0) * 4046.86
        daily_co2_kg_acre = (
            daily_biomass_kg_acre * cls.CARBON_CONTENT_DRY_MATTER * cls.CO2_MOLECULAR_RATIO
        )

        total_farm_daily_co2_kg = daily_co2_kg_acre * farm_acres

        # Market valuation ($15 per ton of verified soil CO2 credit)
        carbon_credit_usd_value = (total_farm_daily_co2_kg / 1000.0) * 15.00
        carbon_credit_kes_value = carbon_credit_usd_value * 130.0 # ~130 KES/USD

        return {
            "crop_type": crop_key,
            "RUE_g_MJ": rue,
            "PAR_energy_MJ_m2": round(par_energy, 2),
            "daily_biomass_kg_acre": round(daily_biomass_kg_acre, 2),
            "daily_co2_sequestered_kg_acre": round(daily_co2_kg_acre, 2),
            "total_farm_daily_co2_kg": round(total_farm_daily_co2_kg, 2),
            "estimated_credit_value_usd": round(carbon_credit_usd_value, 4),
            "estimated_credit_value_kes": round(carbon_credit_kes_value, 2),
        }

    @staticmethod
    def evaluate_parametric_insurance_trigger(
        consecutive_dry_days: int,
        mean_solar_irradiance_W_m2: float,
        rainfall_7_days_mm: float
    ) -> Dict[str, Any]:
        """
        Evaluates weather-index drought parameters.
        Triggers automatic payout if solar stress threshold > 950 W/m^2 for > 7 dry days.
        """
        STRESS_IRRADIANCE_THRESHOLD = 950.0 # W/m^2
        MAX_DRY_DAYS_ALLOWED = 7

        is_high_solar_stress = mean_solar_irradiance_W_m2 >= STRESS_IRRADIANCE_THRESHOLD
        is_water_deficient = rainfall_7_days_mm < 5.0
        is_threshold_exceeded = (
            consecutive_dry_days >= MAX_DRY_DAYS_ALLOWED and is_high_solar_stress and is_water_deficient
        )

        if is_threshold_exceeded:
            status = "CLAIM_TRIGGERED"
            payout_amount_kes = 15000.0 # Instant micro-payout per acre
            message_en = f"Drought threshold breached ({consecutive_dry_days} days high solar flux). Instant claim issued."
            message_sw = f"Kiwango cha ukame kimevukwa (siku {consecutive_dry_days} za jua kali). Malipo yameidhinishwa."
        else:
            status = "MONITORING_ACTIVE"
            payout_amount_kes = 0.0
            message_en = f"Climate parameters within normal bounds. ({consecutive_dry_days}/{MAX_DRY_DAYS_ALLOWED} dry days)."
            message_sw = f"Hali ya hewa ni ya kawaida. (Siku {consecutive_dry_days}/{MAX_DRY_DAYS_ALLOWED} za ukame)."

        return {
            "status": status,
            "consecutive_dry_days": consecutive_dry_days,
            "mean_solar_flux_W_m2": mean_solar_irradiance_W_m2,
            "payout_triggered": is_threshold_exceeded,
            "payout_amount_kes": payout_amount_kes,
            "message_en": message_en,
            "message_sw": message_sw,
        }

    @staticmethod
    def generate_export_traceability_token(
        farmer_id: str, farm_location: str, water_saved_liters: float
    ) -> Dict[str, str]:
        """
        Mints a cryptographic Real-World Asset (RWA) verification token for European exporters.
        """
        raw_payload = f"{farmer_id}:{farm_location}:{water_saved_liters}:{time.time()}"
        sha256_hash = hashlib.sha256(raw_payload.encode()).hexdigest().upper()
        token = f"EP-RWA-2026-{sha256_hash[:12]}"

        return {
            "export_token": token,
            "verification_url": f"https://e-panda.co.ke/verify/{token}",
            "certification": "Verified Solar-Efficiency & Water-Conserved Agricultural Produce"
        }
