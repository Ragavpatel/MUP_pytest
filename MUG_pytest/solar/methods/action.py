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
    profile_class: int | None = 1,
    reference_year: int | None = 2000,
    value_column: str = "Average"
):

    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%d-%m-%Y")
        end_date = datetime.strptime(end_date, "%d-%m-%Y")
    
    if start_date.month < 2 or (start_date.month == 2 and start_date.day <= 28):
        year_to_check = start_date.year
    else:
        year_to_check = end_date.year

    logging.debug(f"Year to check for leap: {year_to_check}")

    if not is_leap(year_to_check):
        mask_feb29 = ~((df_coefficient[which]['Date'].dt.day == 29) & 
                       (df_coefficient[which]['Date'].dt.month == 2))
    else:
        mask_feb29 = True

    df_coefficient_local = df_coefficient.copy()[which]

    # Make reference year dynamic (default = 2000)
    if reference_year:
        start_date = start_date.replace(year=reference_year)
        end_date = end_date.replace(year=reference_year)

    # Build mask dynamically
    mask_base = mask_feb29
    if profile_class is not None and "ProfileClass" in df_coefficient_local.columns:
        mask_base = mask_base & (df_coefficient_local["ProfileClass"] == profile_class)

    if start_date <= end_date:
        mask = (df_coefficient_local['Date'] >= start_date) & (df_coefficient_local['Date'] <= end_date)
        return df_coefficient_local.loc[mask & mask_base, value_column].tolist()
    else:
        mask1 = df_coefficient_local['Date'] >= start_date
        mask2 = df_coefficient_local['Date'] <= end_date
        part1 = df_coefficient_local.loc[mask1 & mask_base, value_column]
        part2 = df_coefficient_local.loc[mask2 & mask_base, value_column]
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
        col2 = df_raw[sheet_name]["house_usage_kwh"].round(9)

    elif which.lower() == "generation":
        col1 = df_multiplied.round(9)
        col2 = df_raw[sheet_name]["solar_power_generated_kwh"].round(9)

    else:
        raise ValueError(f"Unknown verification type: {which}")

    for idx, (v1, v2) in enumerate(zip(col1, col2)):
        if v1 != v2:
            date_val = df_raw[sheet_name]["date"].iloc[idx]
            slot_val = df_raw[sheet_name]["time_slot_id"].iloc[idx]
            mismatches.append((idx, date_val, slot_val, v1, v2))
            logging.error(f"Row {idx}: Calculated Value: {v1} != Existing value: {v2}")
        else:
            logging.debug(f"Row {idx}: {v1} matches {v2}")

    if mismatches:
        return mismatches
    else:
        logging.info("All rows match perfectly!")
        return "All rows match perfectly!"


def calculate_panel_capacity(fix_panel_capacity,Panel_degradation,df_request,sheet_name):
    df_request = df_request[sheet_name]
    current_year = df_request["date"].dt.year.iloc[0]
    has_feb29 = ((df_request["date"].dt.month == 2) & (df_request["date"].dt.day == 29)).any()

    if is_leap(current_year) and has_feb29:
        days_in_year = 366
    else:
        days_in_year = 365

    print(f"Days in year used: {days_in_year}")

    degradation_rate = Panel_degradation / 100

    degradation = round((degradation_rate / days_in_year) * fix_panel_capacity, 9)
    values = []
    period = 0

    while fix_panel_capacity - degradation * (period // 48) > 0:
        if period < 48:
            value = fix_panel_capacity
        else:
            value = fix_panel_capacity - degradation * (period // 48)
        values.append(value)
        period += 1

    return pd.DataFrame({"PanelCapacity": values})