"""
===============================================================================
e-Panda Backend Engine: FAO-56 Evapotranspiration & Hydration Module
Author: Elisha Ochieng' Alal
Description: Translates solar irradiance (MJ/m^2/day) into reference 
             evapotranspiration (ETo) and dynamic crop water requirements (ETc).
===============================================================================
"""

import math
from typing import Dict, Any


class AgronomicEngine:
    # Dynamic Crop Coefficients (Kc) across growth stages
    CROP_COEFFICIENTS: Dict[str, Dict[str, float]] = {
        "AVOCADO": {"initial": 0.60, "mid_season": 0.85, "late_season": 0.75},
        "ROSE": {"initial": 0.80, "mid_season": 1.10, "late_season": 0.95},
        "TEA": {"initial": 0.90, "mid_season": 1.15, "late_season": 1.00},
        "COFFEE": {"initial": 0.70, "mid_season": 1.05, "late_season": 0.90},
        "MAIZE": {"initial": 0.30, "mid_season": 1.20, "late_season": 0.60},
    }

    # Soil Water Retention Capacity Factors (Sw)
    SOIL_FACTORS: Dict[str, float] = {
        "SANDY": 1.15,    # Rapid drainage requires +15% water buffer
        "LOAM": 1.00,     # Standard baseline
        "CLAY": 0.88,     # High moisture retention reduces net demand
        "VOLCANIC": 0.95, # Common in Central Kenyan Highlands
    }

    @staticmethod
    def calculate_reference_evapotranspiration_fao56(
        solar_radiation_MJ_m2: float,
        temp_mean_c: float,
        wind_speed_m_s: float = 2.0,
        relative_humidity: float = 65.0
    ) -> float:
        """
        Calculates reference evapotranspiration ETo (mm/day) using simplified
        Hargreaves-Samani / Radiation-based FAO-56 formulation:
        ETo = 0.0023 * (T_mean + 17.8) * (T_max - T_min)^0.5 * R_s_equivalent
        """
        # Approximating radiation thermal equivalent
        # 1 MJ/m^2/day corresponds to ~0.408 mm/day of water evaporation
        radiation_evap_equivalent = 0.408 * solar_radiation_MJ_m2
        
        # Temperature vapor pressure gradient factor
        temp_factor = (temp_mean_c + 17.8) / 100.0
        
        # Humidity and wind speed scaling
        humidity_adjustment = 1.0 + (100.0 - relative_humidity) * 0.003
        wind_adjustment = 1.0 + (wind_speed_m_s * 0.05)
        
        ETo = radiation_evap_equivalent * temp_factor * humidity_adjustment * wind_adjustment
        return max(0.5, round(ETo, 2))

    @classmethod
    def calculate_crop_water_requirement(
        cls,
        solar_radiation_MJ_m2: float,
        crop_type: str,
        growth_stage: str,
        soil_type: str,
        temp_c: float,
        rainfall_mm: float = 0.0,
        operating_mode: str = "GROWTH" # "GROWTH" or "DROUGHT"
    ) -> Dict[str, Any]:
        """
        Calculates Net Irrigation Requirement (NIR) in mm/day and liters/plant.
        """
        crop_key = crop_type.upper()
        stage_key = growth_stage.lower()
        soil_key = soil_type.upper()

        # Fetch Kc coefficient
        kc = cls.CROP_COEFFICIENTS.get(crop_key, {}).get(stage_key, 0.85)
        sw = cls.SOIL_FACTORS.get(soil_key, 1.0)

        # 1. Calculate Reference ETo
        ETo = cls.calculate_reference_evapotranspiration_fao56(
            solar_radiation_MJ_m2=solar_radiation_MJ_m2,
            temp_mean_c=temp_c
        )

        # 2. Crop Evapotranspiration ETc = Kc * ETo
        ETc = ETo * kc

        # 3. Effective Rainfall Deduction (P_eff)
        # USDA SCS Method: P_eff = P * (125 - 0.2 * P) / 125 for P <= 250mm
        if rainfall_mm > 0:
            P_eff = max(0.0, rainfall_mm * 0.75)
        else:
            P_eff = 0.0

        # 4. Net Irrigation Requirement (NIR)
        raw_nir = max(0.0, ETc - P_eff) * sw

        # 5. Apply Operating Mode Scaling
        if operating_mode.upper() == "DROUGHT":
            # Deficit Irrigation Mode: 60% of full NIR to preserve plant vascular life
            final_nir = raw_nir * 0.60
            water_saved_percent = 40.0
        else:
            final_nir = raw_nir
            water_saved_percent = 0.0

        # Convert mm/day to Liters per plant/tree (assuming 3.5 m^2 canopy area)
        canopy_area_m2 = 3.5
        liters_per_plant = final_nir * canopy_area_m2

        # Convert to manual 20L Jerrycan Pouring Time (standard flow rate ~0.25 L/sec)
        pouring_seconds = math.ceil(liters_per_plant / 0.25)

        return {
            "crop_type": crop_key,
            "growth_stage": stage_key,
            "soil_type": soil_key,
            "operating_mode": operating_mode.upper(),
            "crop_coefficient_kc": kc,
            "soil_factor_sw": sw,
            "ETo_mm_day": ETo,
            "ETc_mm_day": round(ETc, 2),
            "effective_rainfall_mm": round(P_eff, 2),
            "net_irrigation_requirement_mm": round(final_nir, 2),
            "liters_per_plant_day": round(liters_per_plant, 2),
            "manual_pouring_duration_seconds": pouring_seconds,
            "water_saved_percentage": water_saved_percent
        }
