import pandas as pd
from datetime import datetime
import logging
import numpy as np
import calendar
from solar.config import solar_config


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

def get_month_range(start, end):
    months = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]
    i1, i2 = months.index(start), months.index(end)
    if i1 <= i2:
        return months[i1:i2+1]
    else:
        return months[i1:] + months[:i2+1]

def get_coefficient_value(
    start_date, 
    end_date, 
    df_coefficient: pd.DataFrame,
    which,
    value_column: str = "Average"):
    
    days_in_year= days_in_period(solar_config.start_date,solar_config.end_date)
    
    if days_in_year == 365:
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
            return df_coefficient_local.loc[mask & mask_feb29, 'Value']
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
            return df_coefficient_local.loc[mask & (df_coefficient_local["ProfileClass"] == 1) & mask_feb29, value_column]
        else:
            # Wrap-around case 
            mask1 = df_coefficient_local['Date'] >= start_date
            mask2 = df_coefficient_local['Date'] <= end_date
            part1 = df_coefficient_local.loc[mask1 & (df_coefficient_local["ProfileClass"] == 1) & mask_feb29, value_column]
            part2 = df_coefficient_local.loc[mask2 & (df_coefficient_local["ProfileClass"] == 1) & mask_feb29, value_column]
            return pd.concat([part1, part2]).reset_index(drop=True)

def calculate_panel_capacity(no_of_panel, panel_size_kWp, panel_degradation, sheet_name):
    global days_in_year
    
    fix_panel_capacity= no_of_panel * panel_size_kWp
    
    days_in_year= days_in_period(solar_config.start_date,solar_config.end_date)

    degradation_rate = panel_degradation / 100
    
    degradation = round((degradation_rate / days_in_year) * fix_panel_capacity, 9)
    total_periods = days_in_year * 48
    values = []
    period = 0

    while period < total_periods:
        if period < 48:
            value = fix_panel_capacity
        else:
            value = (fix_panel_capacity - degradation * (period // 48))
        values.append(value)
        period += 1
    return pd.DataFrame(values)

def days_in_period(start_date, end_date):

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%d-%m-%Y")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%d-%m-%Y")

    years = range(start_date.year, end_date.year + 1)
    has_leap = any(calendar.isleap(year) for year in years)

    if has_leap:
        days_in_year = 366
    else:
        days_in_year = 365

    logging.info(f"Days in year used: {days_in_year}")
    return days_in_year

def calculate_battery_size(battery_size,battery_degradation_first):
    days_in_year = days_in_period(solar_config.start_date, solar_config.end_date)
    total_periods = days_in_year * 48

    values = []
    period = 0
    while period < total_periods:
        day_count = period // 48

        if period < 48:
            value = battery_size
        else:
            value = battery_size * (battery_degradation_first ** day_count)
        values.append(float(value))
        period += 1
    return pd.DataFrame(values, dtype=float)