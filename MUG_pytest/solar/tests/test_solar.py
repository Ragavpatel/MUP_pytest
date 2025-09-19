import logging,os
import pandas as pd
from solar.methods.utils import *
from solar.methods.action import *

# def test_solar_journey():
#     df_raw_data = loadExcelFile("raw.xlsx")
#     df_coefficient_data = loadExcelFile("coefficients.xlsx")
#     logging.info(f"Raw data fetched - {df_coefficient_data}")
#     # df_coefficient_data = fetch_coefficient_value("solar",
#     #     df_coefficient_data,
#     #     "2000-03-01",
#     #     "2000-02-01"
#     # )
#     #calculate_consumption(df_coefficient_data,df_raw_data )


def test_fetch_solar_coefficient_date_and_value():

    df_current = loadExcelFile("raw_test.xlsx", "Current")
    df_request = loadExcelFile("raw_test.xlsx", "Request")
    df_coefficient = loadExcelFile("coefficients.xlsx", "SolarCoefficient")

    df_raw_dict = {
        "Current": df_current,
        "Request": df_request
    }

    calculate_consumption(df_raw_dict, df_coefficient)