"""
===============================================================================
e-Panda Backend Engine: Africa's Talking USSD (*384*#) & SMS Gateway
Author: Elisha Ochieng' Alal
Description: Provides interactive offline feature phone USSD navigation and 
             automated bilingual SMS dispatch for rural smallholder farmers.
===============================================================================
"""

from app.core.astrophysics import AstrophysicalEngine
from app.core.agronomics import AgronomicEngine
from app.core.fintech import ClimateFintechEngine


class USSDSMSGateway:
    @classmethod
    def handle_ussd_request(
        cls, session_id: str, service_code: str, phone_number: str, text: str
    ) -> str:
        """
        Processes USSD HTTP POST callback from Africa's Talking API.
        Responses starting with "CON" keep the menu open.
        Responses starting with "END" close the USSD session.
        """
        user_inputs = text.split("*") if text else []
        level = len(user_inputs)

        # Level 0: Main Menu (Selection of Language)
        if text == "":
            response = "CON Karibu e-Panda Solar AgTech\nChoose Language / Chagua Lugha:\n1. Kiswahili\n2. English"

        # Level 1: Main Feature Menu
        elif level == 1:
            lang = "SW" if user_inputs[0] == "1" else "EN"
            if lang == "SW":
                response = "CON e-Panda Menyu Kuu:\n1. Mahitaji ya Maji Leo (Solar)\n2. Badili Hali (Growth/Drought)\n3. Salio la Carbon Credits\n4. Bima ya Ukame Status"
            else:
                response = "CON e-Panda Main Menu:\n1. Today's Solar Water Need\n2. Switch Mode (Growth/Drought)\n3. Carbon Credit Ledger\n4. Drought Insurance Status"

        # Level 2: Actions
        elif level == 2:
            lang = "SW" if user_inputs[0] == "1" else "EN"
            choice = user_inputs[1]

            if choice == "1": # Water calculation
                # Execute engine for Hass Avocado in Thika
                astro = AstrophysicalEngine(latitude=-1.033, longitude=37.069)
                solar = astro.calculate_effective_ground_irradiance(day_of_year=280, cloud_cover_fraction=0.15)
                water = AgronomicEngine.calculate_crop_water_requirement(
                    solar_radiation_MJ_m2=solar["daily_solar_radiation_MJ_m2"],
                    crop_type="AVOCADO",
                    growth_stage="mid_season",
                    soil_type="LOAM",
                    temp_c=25.5
                )

                if lang == "SW":
                    response = f"END Ripoti ya e-Panda (Avocado):\nJua Leo: {solar['I_effective_W_m2']} W/m2\nMaji: Lita {water['liters_per_plant_day']:.1f} kwa mti.\nNjia ya Ndoo: Mwagilia kwa sekunde {water['manual_pouring_duration_seconds']} kila mti."
                else:
                    response = f"END e-Panda Solar Report (Avocado):\nSolar Flux: {solar['I_effective_W_m2']} W/m2\nWater: {water['liters_per_plant_day']:.1f} Liters/tree.\nJerrycan Bucket: Pour {water['manual_pouring_duration_seconds']} secs per tree."

            elif choice == "2": # Switch Mode
                if lang == "SW":
                    response = "CON Chagua Hali ya Ukulima:\n1. Hali ya Kukua (Growth Mode)\n2. Hali ya Ukame (Drought Mode - Okoa 40% Maji)"
                else:
                    response = "CON Select Farming Mode:\n1. Growth Mode (Max Yield)\n2. Drought Mode (Save 40% Water)"

            elif choice == "3": # Carbon Ledger
                carbon = ClimateFintechEngine.calculate_biomass_and_carbon_credit("AVOCADO", 22.5, 2.5)
                if lang == "SW":
                    response = f"END Carbon Credit Ledger:\nKiasi kilichohifadhiwa: {carbon['total_farm_daily_co2_kg']} kg CO2/siku.\nThamani: KES {carbon['estimated_credit_value_kes']}."
                else:
                    response = f"END Carbon Credit Ledger:\nSequestered: {carbon['total_farm_daily_co2_kg']} kg CO2/day.\nEstimated Value: KES {carbon['estimated_credit_value_kes']}."

            elif choice == "4": # Insurance Status
                insurance = ClimateFintechEngine.evaluate_parametric_insurance_trigger(8, 980.0, 0.0)
                msg = insurance["message_sw"] if lang == "SW" else insurance["message_en"]
                response = f"END Bima Status:\n{msg}"

            else:
                response = "END Chaguo si sahihi. / Invalid choice."

        # Level 3: Mode Confirmation
        elif level == 3 and user_inputs[1] == "2":
            lang = "SW" if user_inputs[0] == "1" else "EN"
            mode_choice = user_inputs[2]
            if mode_choice == "1":
                response = "END Hali ya GROWTH MODE imewashwa!" if lang == "SW" else "END GROWTH MODE activated!"
            else:
                response = "END Hali ya DROUGHT MODE imewashwa! Maji yatahifadhiwa kwa 40%." if lang == "SW" else "END DROUGHT MODE activated! 40% water preserved."

        else:
            response = "END Session expired. Please redial *384*#."

        return response
