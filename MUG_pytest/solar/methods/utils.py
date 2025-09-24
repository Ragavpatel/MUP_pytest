import pandas as pd
import os
import logging
from solar.methods.action import *
from solar.methods.generate_report import *

def loadExcelFile(filename):
    return pd.read_excel(os.getcwd()+"\solar\\testData\\"+filename, sheet_name=None)
    
def calculate_consumption(df_raw, df_coefficient):
    startdate = fetch_date(df_raw,"Current","startDate")
    enddate = fetch_date(df_raw,"Current","endDate")
    ElectricityConsumption = get_electricity_consumption(df_raw, "Request")
    df_coefficient_average = get_coefficient_value(startdate,enddate,df_coefficient, "ElectricityCoefficient",1,2000)

    logging.info(f"Startdate is: {startdate}")
    logging.info(f"Enddate is: {enddate}")
    logging.info(f"ElectricityConsumption value: {ElectricityConsumption.tolist()}")
    logging.debug(f"Coefficient value capture is: {df_coefficient_average.iloc[0]}")
    
    df_calculated_coefficient = df_coefficient_average*ElectricityConsumption
    logging.info("Calculated Consumption completed!")
    return df_calculated_coefficient

def verify_with_raw_data(df_calculated, df_raw, sheet_name, which):
    return verify_calculated_consumption(df_calculated,df_raw,sheet_name,which )


def calculate_generation(df_raw, df_coefficient):
    startdate = fetch_date(df_raw, "Current", "startDate")
    enddate = fetch_date(df_raw, "Current", "endDate")

    df_coefficient_average = get_coefficient_value(startdate, enddate, df_coefficient, "SolarCoefficient")

    No_Of_panel = fetch_data_from_df(df_raw, "Request", "NoOfPanel")
    Panel_size_kWp = fetch_data_from_df(df_raw,"Request","PanelSize_kWp")
    Panel_irradiance = fetch_data_from_df(df_raw,"Request","PanelIrradiance")
    Panel_degradation = fetch_data_from_df(df_raw,"Request","PanelDegradationPctYr1")

    fix_panel_capacity = No_Of_panel * Panel_size_kWp
    panel_capacity_df = calculate_panel_capacity(fix_panel_capacity,Panel_degradation,df_raw,"Current")

    # Align lengths
    min_len = min(len(df_coefficient_average), len(panel_capacity_df))
    df_result = pd.DataFrame({
        "SolarCoefficient": df_coefficient_average[:min_len],
        "PanelCapacity": panel_capacity_df["PanelCapacity"][:min_len],
    })
    df_result["CalculatedSolarGeneration"] = (
        df_result["SolarCoefficient"] * df_result["PanelCapacity"] * Panel_irradiance
    )

    logging.info("Calculated Solar Generation completed!")
    # Return the numeric Series expected by verification logic
    return df_result["CalculatedSolarGeneration"]


def fetch_data_from_df(df, sheet_name, col_name):
    df_sheet = df[sheet_name]
    matched_cols = [c for c in df_sheet.columns if c.lower() == col_name.lower()]
    if not matched_cols:
        raise ValueError(f"Column '{col_name}' not found in sheet '{sheet_name}'.")
    col = matched_cols[0]

    df_clean = df_sheet.dropna(subset=[col])
    if df_clean.empty:
        raise ValueError(f"No valid value found for column '{col_name}' in sheet '{sheet_name}'.")

    value = df_clean[col].iloc[0]
    return value



def get_user_data(df):
    customer_id = fetch_data_from_df(df,"Request","customerId")
    Quote_id = fetch_data_from_df(df,"Request","QuoteId")

    user_info = {
        "customerId": customer_id,
        "QuoteId": Quote_id
    }
    return user_info

def generate_report(df,exceution):
    user_info = get_user_data(df)
    generate_html_report(user_info,exceution)