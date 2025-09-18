import logging,os
from solar.methods.utils import loadExcelFile

def test_solar_journey():
    # df_raw_data = loadExcelFile("raw.xlsx")
    df_coefficient_data = loadExcelFile("coefficients.xlsx")
    logging.info(f"Raw data fetched - {df_coefficient_data}")

