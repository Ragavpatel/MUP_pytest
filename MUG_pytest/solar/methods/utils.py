import pandas as pd
import os
import logging
from solar.methods.action import *

def loadExcelFile(filename):
    return pd.read_excel(os.getcwd()+"\solar\\testData\\"+filename, sheet_name=None)
    
def calculate_consumption(df_raw, df_coefficient):
    startdate = fetch_date(df_raw,"Current","startDate")
    enddate = fetch_date(df_raw,"Current","endDate")
    ElectricityConsumption = get_electricity_consumption(df_raw, "Request")
    df_coefficient_average = get_coefficient_value(startdate,enddate,df_coefficient, "ElectricityCoefficient")

    logging.info(f"Startdate is: {startdate}")
    logging.info(f"Enddate is: {enddate}")
    logging.info(f"ElectricityConsumption value: {ElectricityConsumption.tolist()}")
    logging.debug(f"Coefficient value capture is: {df_coefficient_average.iloc[0]}")
    
    df_calculated_coefficient = df_coefficient_average*ElectricityConsumption
    logging.info("Calculated Consumption completed!")
    return df_calculated_coefficient

def verify_with_raw_data(df_calculated, df_raw, sheet_name, which):
    verify_calculated_consumption(df_calculated,df_raw,sheet_name,which )
    