import pandas as pd
import os
from typing import Optional, Union
from datetime import datetime

def fetch_date(df_raw: dict, which: str = "start"):
    df_current = df_raw.get("Current")
    if df_current is None or df_current.empty:
        return None

    df_current['date'] = pd.to_datetime(df_current['date'], errors='coerce')
    df_current = df_current.dropna(subset=['date'])

    if which.lower() == "start":
        return df_current['date'].iloc[0].strftime("%d-%m-%Y")
    elif which.lower() == "end":
        return df_current['date'].iloc[-1].strftime("%d-%m-%Y")
    else:
        raise ValueError("Parameter 'which' must be 'start' or 'end'.")


def fetch_coefficient_value(
    type,
    df: pd.DataFrame, 
    start_date: str = "", 
    end_date: str = "", 
    value_column: str = "Average"
) -> pd.DataFrame:
    df = df.copy()
    if "Date" not in df.columns:
        raise KeyError("Column 'Date' not found in DataFrame")

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    if start_date and end_date:
        start = datetime.strptime(start_date, "%d-%m-%Y")
        end = datetime.strptime(end_date, "%d-%m-%Y")

        df = df.sort_values(by="Date").reset_index(drop=True)
        start_idx = df.index[df['Date'] >= start].min()

        if pd.isna(start_idx):
            start_idx = 0

        df = pd.concat([df.iloc[start_idx:], df.iloc[:start_idx]])
        df = df[df['Date'] >= start] if start <= end else df
        mask_until_end = (df['Date'] <= end) | (df['Date'] >= start)
        df = df.loc[mask_until_end]

    df['Date'] = df['Date'].dt.strftime("%d-%m-%Y")

    columns_to_return = ['Date']
    if value_column in df.columns:
        columns_to_return.append(value_column)

    if 'TimeSlotId' in df.columns:
        columns_to_return.append('TimeSlotId')

    return df[columns_to_return].reset_index(drop=True)



def get_coefficient_value(startdate,enddate,df_coefficient):
    df_coefficient_values = fetch_coefficient_value(
        type=None,
        df=df_coefficient,
        start_date="03-09-2000",
        end_date="02-09-2000"
    )

    df_result = df_coefficient[['TimeSlotId', 'Average']].reset_index(drop=True)
    return df_result


def get_electricity_consumption(df_request, sheet_name):
    df_request = df_request[sheet_name]
    df_clean = df_request.dropna(subset=["ElectricityConsumption"])
    if df_clean.empty:
        raise ValueError("No valid ElectricityConsumption value found in Request sheet.")

    return df_clean["ElectricityConsumption"].iloc[0]



def Assert_usage_kwh_and_calculate_consumption_coeff(df_current, sheet_name):
    df_current = df_current[sheet_name]
    