import logging,os
from solar.methods.utils import *

def test_solar_journey():
    df_raw_data = loadExcelFile("raw.xlsx")
    df_coefficient_data = loadExcelFile("coefficients.xlsx")
    logging.info(f"Coefficient data fetched fetched")
    logging.debug(f"Coefficient data fetched - {df_coefficient_data}")
    df_calculated_coefficient = calculate_consumption(df_raw_data, df_coefficient_data)
    verify_with_raw_data(df_calculated_coefficient, df_raw_data, "Current", "consumption")	