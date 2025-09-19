import pandas as pd
import os
from typing import Optional, Union
from datetime import datetime
from solar.methods.action import *

def loadExcelFile(filename: str, sheet_name: Optional[Union[str, int, list]] = None):
    file_path = os.path.join(os.getcwd(), "solar", "testData", filename)
    return pd.read_excel(file_path, sheet_name=sheet_name)


# def calculate_consumption(df_raw: dict, df_coefficient: pd.DataFrame):
   
#     df_current = df_raw["Current"]
#     df_request = df_raw["Request"]


#     df_current['date'] = pd.to_datetime(df_current['date'], errors='coerce')
#     df_current = df_current.dropna(subset=['date'])
#     start_date = df_current['date'].iloc[0].strftime("%d-%m-%Y")
#     end_date   = df_current['date'].iloc[-1].strftime("%d-%m-%Y")

#     #consumption_coeff = df_coefficient["Average"].iloc[0]
#     consumption_coeff = df_current['Consumption Coeff']
    
#     df_request['calculated_coeff'] = pd.to_numeric(df_request['ElectricityConsumption'], errors='coerce') * consumption_coeff
#     df_current['calculated_coeff'] = df_request['calculated_coeff'].values[:len(df_current)]


#     df_current['date'] = df_current['date'].dt.strftime("%d-%m-%Y")



#     testdata_folder = os.path.join(os.getcwd(), "solar", "testData")
#     output_path = os.path.join(testdata_folder, "raw_output.xlsx")

#     with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
#         df_current.to_excel(writer, sheet_name="Current", index=False)
#         df_request.to_excel(writer, sheet_name="Request", index=False)
#         df_coefficient.to_excel(writer, sheet_name="SolarCoefficient", index=False)

#     print(f"Output temporarily saved to: {output_path}")

#     return df_request, start_date, end_date, consumption_coeff




def calculate_consumption(df_raw: dict, df_coefficient: pd.DataFrame):

    startdate = fetch_date(df_raw,"start")
    enddate = fetch_date(df_raw,"end")
    ElectricityConsumption = get_electricity_consumption(df_raw, "Request")
    df_coefficient_list = get_coefficient_value(startdate,enddate,df_coefficient)

    calculate_consumption_coeff = ElectricityConsumption * df_coefficient_list['Average']

    Assert_usage_kwh_and_calculate_consumption_coeff(df_raw, "Current")

   
    print(f"startdate: {startdate}")
    print(f"enddate: {enddate}")
    print(f"ElectricityConsumption: {ElectricityConsumption}")

    print("\n🔹 calculated consumption coeff")
    print(calculate_consumption_coeff)

    # print("\n🔹 TimeSlotId Column:")
    # print(df_coefficient_list['TimeSlotId'])

    # print("\n🔹 Average Column:")
    # print(df_coefficient_list['Average'])