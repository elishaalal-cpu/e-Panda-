"""
===============================================================================
e-Panda Backend Engine: SQLAlchemy Database Models
Author: Elisha Ochieng' Alal
Description: Database schemas for farmers, farm plots, irrigation events, 
             and carbon ledger tracking.
===============================================================================
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class FarmerModel(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    county_location = Column(String(50), default="Kiambu")
    preferred_language = Column(String(10), default="SW") # "SW" or "EN"
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)


class FarmPlotModel(Base):
    __tablename__ = "farm_plots"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, nullable=False)
    crop_type = Column(String(50), default="AVOCADO")
    growth_stage = Column(String(50), default="mid_season")
    soil_type = Column(String(50), default="LOAM")
    farm_size_acres = Column(Float, default=1.0)
    operating_mode = Column(String(20), default="GROWTH") # "GROWTH" or "DROUGHT"


class IrrigationLogModel(Base):
    __tablename__ = "irrigation_logs"

    id = Column(Integer, primary_key=True, index=True)
    farm_plot_id = Column(Integer, nullable=False)
    solar_irradiance_W_m2 = Column(Float)
    evapotranspiration_mm = Column(Float)
    water_applied_liters = Column(Float)
    carbon_sequestered_kg = Column(Float)
    logged_at = Column(DateTime, default=datetime.datetime.utcnow)
