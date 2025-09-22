import pandas as pd
from datetime import datetime
import logging
import numpy as np

def fetch_date(df_raw, sheet_name, which):
    df_sheet_name = df_raw.get(sheet_name)
    if df_sheet_name is None or df_sheet_name.empty:
        return None

    df_sheet_name['date'] = pd.to_datetime(df_sheet_name['date'], errors='coerce')
    df_sheet_name = df_sheet_name.dropna(subset=['date'])

    if which.lower() == "startdate":
        return df_sheet_name['date'].iloc[0].strftime("%d-%m-%Y")
    elif which.lower() == "enddate":
        return df_sheet_name['date'].iloc[-1].strftime("%d-%m-%Y")
    else:
        logging.error("Parameter 'which' must be 'start' or 'end'.")
        raise ValueError("Parameter 'which' must be 'start' or 'end'.")

def is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def get_coefficient_value(
    start_date, 
    end_date, 
    df_coefficient: pd.DataFrame,
    which,
    value_column: str = "Average"):
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%d-%m-%Y")
        end_date = datetime.strptime(end_date, "%d-%m-%Y")
    
    if start_date.month < 2 or (start_date.month == 2 and start_date.day <= 28):
        year_to_check = start_date.year
        logging.debug(f"Year to check for leap : {year_to_check}")
    else:
        year_to_check = end_date.year
        logging.debug(f"Year to check for leap : {year_to_check}")
    
    if not is_leap(year_to_check):
        mask_feb29 = ~((df_coefficient[which]['Date'].dt.day == 29) & (df_coefficient[which]['Date'].dt.month == 2))
    else:
        mask_feb29 = True
    
    if which.lower() == "solarcoefficient":
        df_coefficient_local = df_coefficient.copy()
        df_coefficient_local= df_coefficient_local[which]
        
        start_date = start_date.replace(year=2000)
        end_date = end_date.replace(year=2000)
        
        if start_date <= end_date:
            # Normal case
            mask = (df_coefficient_local['Date'] >= start_date) & (df_coefficient_local['Date'] <= end_date)
            return df_coefficient_local.loc[mask & mask_feb29, 'Value'].tolist()
        else:
            # Wrap-around case
            mask1 = df_coefficient_local['Date'] >= start_date
            mask2 = df_coefficient_local['Date'] <= end_date
            part1 = df_coefficient_local.loc[mask1 & mask_feb29, value_column]
            part2 = df_coefficient_local.loc[mask2 & mask_feb29, value_column]
            return pd.concat([part1, part2]).reset_index(drop=True)
        
    elif which.lower() == "electricitycoefficient":
        df_coefficient_local = df_coefficient.copy()
        df_coefficient_local= df_coefficient_local[which]
        
        start_date = start_date.replace(year=2000)
        end_date = end_date.replace(year=2000)
        
        if start_date <= end_date:
            # Normal case
            mask = (df_coefficient_local['Date'] >= start_date) & (df_coefficient_local['Date'] <= end_date)
            return df_coefficient_local.loc[mask & (df_coefficient_local["ProfileClass"] == 1) & mask_feb29, value_column].tolist()
        else:
            # Wrap-around case
            mask1 = df_coefficient_local['Date'] >= start_date
            mask2 = df_coefficient_local['Date'] <= end_date
            part1 = df_coefficient_local.loc[mask1 & (df_coefficient_local["ProfileClass"] == 1) & mask_feb29, value_column]
            part2 = df_coefficient_local.loc[mask2 & (df_coefficient_local["ProfileClass"] == 1) & mask_feb29, value_column]

            return pd.concat([part1, part2]).reset_index(drop=True)

def get_electricity_consumption(df_request, sheet_name):
    df_request = df_request[sheet_name]
    df_clean = df_request.dropna(subset=["ElectricityConsumption"])
    if df_clean.empty:
        raise ValueError("No valid ElectricityConsumption value found in Request sheet.")

    return df_clean["ElectricityConsumption"].iloc[0]

def verify_calculated_consumption(df_multiplied, df_raw, sheet_name, which):
    mismatches = []

    if which.lower() == "consumption":
        col1 = df_multiplied.round(9)
        col2 = df_raw[sheet_name]["house_usage_kwh"]

    for idx, (v1, v2) in enumerate(zip(col1, col2)):
        if np.isclose(v1, v2):
            logging.debug(f" Row {idx}: Calculated Value: {v1} matches Existing value: {v2}")
        else:
            logging.error(f" Row {idx}: Calculated Value: {v1} != Existing value: {v2}")
            mismatches.append(idx)

    if mismatches:
        logging.debug(f"\n Total mismatched rows: {len(mismatches)} → {mismatches}")
    else:
        logging.info(" All rows match perfectly!")