import pandas as pd
import os
import logging
from solar.methods.actions import *
from solar.api.apiRequest import apiRequestHandler, apiResponseHandler
from solar.config import solar_config
from solar.methods.state_manager import StateManager
from datetime import datetime, timedelta


def loadExcelFile(filename):
    return pd.read_excel(os.getcwd()+"\solar\\testData\\"+filename, sheet_name=None)
    
def get_and_set_data_from_quoteId():
    quoteId = solar_config.quoteid
    token = apiRequestHandler.get_token()
    response = apiRequestHandler.get_data_from_quoteid(quoteId, token)
    apiResponseHandler.set_data_from_quoteid_response(response)
    
    return response.json()

def calculate_consumption(df_coefficient):
    startdate = datetime.strptime(solar_config.start_date, "%d-%m-%Y")
    enddate = datetime.strptime(solar_config.end_date, "%d-%m-%Y")
    
    electricityConsumption= StateManager.get_value("_electricityConsumption")
    df_coefficient_average = get_coefficient_value(startdate,enddate,df_coefficient, "ElectricityCoefficient")

    logging.info(f"Startdate is: {startdate}")
    logging.info(f"Enddate is: {enddate}")
    logging.debug(f"Coefficient value capture is: {df_coefficient_average.iloc[0]}")
    
    df_calculated_consumption = df_coefficient_average*electricityConsumption
    logging.info("Calculated Consumption completed!")
    
    date_column = get_date_colom(len(df_calculated_consumption),startdate)
 
    df_calculated_consumption = pd.DataFrame({
        "Date": date_column,
        "consumption": df_calculated_consumption
    })
    
    
    return df_calculated_consumption

def calculate_generation(df_coefficient):
    startdate = datetime.strptime(solar_config.start_date, "%d-%m-%Y")
    enddate = datetime.strptime(solar_config.end_date, "%d-%m-%Y")
 
    df_coefficient_average = get_coefficient_value(startdate, enddate, df_coefficient, "SolarCoefficient")
 
    no_of_panel = StateManager.get_value("_noOfPanel")
    panel_size_kWp = StateManager.get_value("_panelSizeKWH")
    panel_irradiance = StateManager.get_value("_panelIrradiance")
    panel_degradation_first = StateManager.get_value("_solarDegradationFirst")
 
    df_panel_capacity = calculate_panel_capacity(no_of_panel, panel_size_kWp, panel_degradation_first, "Current")
    df_calculated_generation = df_coefficient_average.astype(float) * df_panel_capacity.iloc[:, 0].astype(float)
    df_calculated_generation= df_calculated_generation.astype(float) * float(panel_irradiance.split("Irradiance :")[1].strip())
    logging.info("Calculated Solar Generation completed!")
    
    
    date_column = get_date_colom(len(df_calculated_generation),startdate)
 
    df_calculated_generation = pd.DataFrame({
        "Date": date_column,
        "generation": df_calculated_generation
        
    })
    return df_calculated_generation

def verify_calculated_with_api(df_calculated, which):
    if which.lower() == "consumption":
        logging.info(f"Calculated consumption is: {df_calculated}")
        logging.info(f"API consumption is: {StateManager.get_value('_houseHoldConsumption')}")
        assert np.isclose(df_calculated, StateManager.get_value('_houseHoldConsumption'), rtol=1e-9, atol=1e-6), f"Values differ: {df_calculated} vs {StateManager.get_value('_houseHoldConsumption')}"
    elif which.lower() == "generation":
        logging.info(f"Calculated generation is: {df_calculated}")
        logging.info(f"API generation is: {StateManager.get_value('_solarGeneration')}")
        assert np.isclose(df_calculated.round(3), StateManager.get_value('_solarGeneration'), rtol=1e-9, atol=1e-6), f"Values differ: {df_calculated} vs {StateManager.get_value('_solarGeneration')}"
       
    logging.info(f"Verifed both calculation for {which}.")
    
def calculate_battery_capacity():
    battery_size = StateManager.get_value("_batterySize")                          
    battery_degradation_first = StateManager.get_value("_batteryDegradation")  
    battery_usage_first = StateManager.get_value("_batteryUsagePct")         
    battery_usage = battery_usage_first/100

    df_battery_size = calculate_battery_size(battery_size,battery_degradation_first)
    df_calculate_battery_capacity = float(battery_usage) * df_battery_size.iloc[:, 0].astype(float)
    logging.info(f"df_calculate_battery_capacity: {df_calculate_battery_capacity}")
    return df_calculate_battery_capacity

def get_date_colom(length, startdate):
    return [(startdate + timedelta(days=i // 48)).strftime("%d-%m-%Y") for i in range(length)]

def generate_time_slots(days):
    time_slots = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
    return time_slots * days

def filter_by_month(df, month_name):
    return df[pd.to_datetime(df["Date"], format="%d-%m-%Y").dt.month == month_name]
 
def verify_calculated_with_api_monthly(df, data, coloum_name):
    api_attribute = data["calculatedResults"][1]["electricity"]["monthlyBreakDowns"]
    if coloum_name.lower() == "consumption":
        attribute = "householdConsumption"
    if coloum_name.lower() == "generation":
        attribute = "solarGeneration"
    
    for month in range(1, 13):
        # Filter df where Date column's month matches
        monthly_df = filter_by_month(df, month)
        logging.info(f"Calculated value for month {month}: {monthly_df[coloum_name].sum().round(3)} and Api value for month {month}: {api_attribute[month-1][attribute]}")
        assert monthly_df[coloum_name].sum().round(3) == api_attribute[month-1][attribute]
 
def get_unitRate_dataframe(import_data, which, type, isCurrent=None):

    for index in import_data["calculatedResults"]:
        if index["isCurrent"]:
            current = 0
            proposed = 1
        elif():
            current = 1
            proposed = 0
        break  


    if which.lower() == "current":
        if type.lower() == "import":
            data = import_data["calculatedResults"][current]["electricity"]["importRates"]
        elif type.lower() == "export":
            data = import_data["calculatedResults"][current]["electricity"]["exportRates"]
    elif which.lower() == "proposed":
        if type.lower() == "import":
            data = import_data["calculatedResults"][proposed]["electricity"]["importRates"]
        elif type.lower() == "export":
            data = import_data["calculatedResults"][proposed]["electricity"]["exportRates"]        
            
    days = days_in_period(solar_config.start_date,solar_config.end_date)

    # generate Date column
    date_list = get_date_colom(48*days, datetime.strptime(solar_config.start_date, "%d-%m-%Y"))

    # generate Time column using your generate_time_slots function
    time_list = generate_time_slots(days)

    # create dataframe
    df = pd.DataFrame({
        "Date": date_list,
        "Time": time_list
    })
    df["Month"] = pd.to_datetime(df["Date"]).dt.month_name()
    df["UnitRate"] = None
    df["DisplayName"] = None

    
    # Process each rate and assign UnitRate and DisplayName
    for rate in data:
        name = rate["displayName"]
        unit = rate["unitRate"]
        for slot in rate["timeSlot"]:
            months = get_month_range(slot["monthFrom"], slot["monthTo"])
            start_time = slot["timeFrom"]
            end_time = slot["timeTo"]

            # month mask
            month_mask = df["Month"].isin(months)

            # time mask (string comparison works for HH:MM)
            if end_time == "00:00":
                time_mask = df["Time"] >= start_time
            else:
                time_mask = (df["Time"] >= start_time) & (df["Time"] < end_time)

            mask = month_mask & time_mask
            df.loc[mask, ["UnitRate", "DisplayName"]] = [unit, name]

    return df[["Date", "Time", "DisplayName", "UnitRate"]]


def build_power_flow_dataframes(df_consumption: pd.DataFrame, df_generation: pd.DataFrame, df_unit_rates: pd.DataFrame | None = None):
    
    df_c = df_consumption.reset_index(drop=True).copy()
    df_g = df_generation.reset_index(drop=True).copy()

    if len(df_c) != len(df_g):
        raise ValueError("df_consumption and df_generation must have the same number of rows for slot-wise operations")

    # Base columns to carry over if present
    date_series = df_c["Date"] if "Date" in df_c.columns else pd.Series([None] * len(df_c))

    # Initialize outputs to zero
    zero_series = pd.Series([0.0] * len(df_c))

    df_power_purchase = pd.DataFrame({
        "Date": date_series,
        "power_purchased_from_grid_kwh_new": zero_series.copy()
    })

    df_power_sold = pd.DataFrame({
        "Date": date_series,
        "power_sold_kwh_new": zero_series.copy()
    })

    df_power_put_in_battery = pd.DataFrame({
        "Date": date_series,
        "power_put_in_battery_kwh_new": zero_series.copy()
    })

    df_power_pull_in_battery = pd.DataFrame({
        "Date": date_series,
        "power_pull_from_battery_kwh_new": zero_series.copy()
    })

    df_cumulative_battery = pd.DataFrame({
        "Date": date_series,
        "battery_energy_kwh_cumulative": zero_series.copy()
    })

    # First condition
    if "consumption" not in df_c.columns:
        raise ValueError("df_consumption must include a 'consumption' column")
    if "generation" not in df_g.columns:
        raise ValueError("df_generation must include a 'generation' column")

    need_from_grid = (df_c["consumption"] > df_g["generation"]).astype(bool)

    # battery is zero initially, so the mask is exactly the condition above
    purchase_amount = (df_c["consumption"] - df_g["generation"]).clip(lower=0)
    df_power_purchase.loc[need_from_grid, "power_purchased_from_grid_kwh_new"] = purchase_amount[need_from_grid]

    return (
        df_power_purchase,
        df_power_sold,
        df_power_put_in_battery,
        df_power_pull_in_battery,
        df_cumulative_battery,
    )