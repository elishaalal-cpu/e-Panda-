"""
===============================================================================
e-Panda Backend Engine: Astrophysical Solar Flux Calculation Module
Author: Elisha Ochieng' Alal (IAAC 2026 Pre-Finalist)
Description: Models Earth-Sun orbital mechanics, solar constant variations,
             apparent angular radius, atmospheric air mass path length, and
             cloud transmissivity attenuation.
===============================================================================
"""

import math
from typing import Dict, Any


class AstrophysicalEngine:
    # Physical and Astronomical Constants
    SOLAR_LUMINOSITY: float = 3.828e26      # Watts (L_sun)
    SOLAR_RADIUS: float = 6.963e8          # Meters (R_sun)
    ASTRONOMICAL_UNIT: float = 1.496e11    # Meters (1 AU)
    ECCENTRICITY: float = 0.01672          # Earth orbital eccentricity (e)
    PERIHELION_DAY: int = 3                 # Day of year near perihelion (~Jan 3)

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    def get_day_of_year(self, month: int, day: int) -> int:
        """Calculates day of year (1-366) from month and day."""
        days_in_months = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return sum(days_in_months[:month]) + day

    def calculate_earth_sun_distance(self, day_of_year: int) -> float:
        """
        Calculates instantaneous Earth-Sun orbital distance d_S (meters)
        using Keplerian orbit approximation:
        d_S = a * (1 - e^2) / (1 + e * cos(v))
        where v is the true anomaly.
        """
        # Mean anomaly approximation (radians)
        gamma = 2 * math.pi * (day_of_year - 1) / 365.25
        # True anomaly v approximation
        v = gamma + 2 * self.ECCENTRICITY * math.sin(gamma)
        
        # Orbital distance equation
        d_S = (self.ASTRONOMICAL_UNIT * (1 - self.ECCENTRICITY ** 2)) / (
            1 + self.ECCENTRICITY * math.cos(v)
        )
        return d_S

    def calculate_apparent_solar_radius(self, d_S: float) -> float:
        """
        Calculates solar apparent angular radius theta_S in degrees:
        theta_S = arcsin(R_sun / d_S)
        """
        theta_rad = math.asin(self.SOLAR_RADIUS / d_S)
        return math.degrees(theta_rad)

    def calculate_solar_constant_top_of_atmosphere(self, d_S: float) -> float:
        """
        Calculates extraterrestrial solar irradiance I (W/m^2):
        I = L_sun / (4 * pi * d_S^2)
        """
        return self.SOLAR_LUMINOSITY / (4 * math.pi * (d_S ** 2))

    def calculate_solar_declination(self, day_of_year: int) -> float:
        """
        Calculates solar declination angle delta (radians):
        delta = 23.45 * sin(360/365 * (284 + day_of_year))
        """
        decl_deg = 23.45 * math.sin(math.radians((360 / 365) * (284 + day_of_year)))
        return math.radians(decl_deg)

    def calculate_air_mass_and_zenith(
        self, day_of_year: int, hour_angle: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculates solar zenith angle z and relative air mass path length AM.
        Kasten-Young Air Mass formula:
        AM = 1 / (cos(z) + 0.50572 * (96.07995 - z)^(-1.6364))
        """
        lat_rad = math.radians(self.latitude)
        delta = self.calculate_solar_declination(day_of_year)
        
        # Solar zenith angle cos(z)
        cos_z = math.sin(lat_rad) * math.sin(delta) + math.cos(lat_rad) * math.cos(delta) * math.cos(hour_angle)
        cos_z = max(-1.0, min(1.0, cos_z))  # Clamp
        
        z_rad = math.acos(cos_z)
        z_deg = math.degrees(z_rad)
        
        # Air mass calculation for daytime (z < 90 degrees)
        if z_deg < 89.0:
            am = 1.0 / (math.cos(z_rad) + 0.50572 * ((96.07995 - z_deg) ** -1.6364))
        else:
            am = 38.0  # Horizon optical thickness limit
            
        return {"zenith_deg": z_deg, "air_mass": am}

    def calculate_effective_ground_irradiance(
        self, day_of_year: int, cloud_cover_fraction: float, tau_atm_base: float = 0.75
    ) -> Dict[str, Any]:
        """
        Calculates ground-level effective solar irradiance I_effective (W/m^2)
        factoring in orbital mechanics, zenith air mass, and cloud attenuation:
        I_effective = I * (tau_atm ^ AM) * (1 - 0.75 * C^3)
        """
        d_S = self.calculate_earth_sun_distance(day_of_year)
        theta_S = self.calculate_apparent_solar_radius(d_S)
        I_toa = self.calculate_solar_constant_top_of_atmosphere(d_S)
        
        am_data = self.calculate_air_mass_and_zenith(day_of_year, hour_angle=0.0) # Solar noon peak
        am = am_data["air_mass"]
        
        # Atmospheric attenuation exponent
        tau_attenuated = tau_atm_base ** am
        
        # Cloud fraction attenuation (C in [0.0, 1.0])
        C = max(0.0, min(1.0, cloud_cover_fraction))
        cloud_factor = 1.0 - (0.75 * (C ** 3))
        
        I_effective = I_toa * tau_attenuated * cloud_factor
        
        return {
            "day_of_year": day_of_year,
            "earth_sun_distance_km": round(d_S / 1000.0, 2),
            "apparent_solar_radius_deg": round(theta_S, 4),
            "solar_constant_toa_W_m2": round(I_toa, 2),
            "air_mass_index": round(am, 3),
            "cloud_cover_fraction": C,
            "cloud_factor": round(cloud_factor, 3),
            "I_effective_W_m2": round(I_effective, 2),
            "daily_solar_radiation_MJ_m2": round(I_effective * 0.0864, 2) # Convert W/m2 to MJ/m2/day
        }
