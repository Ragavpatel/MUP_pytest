import logging,os
from solar.methods.utils import *

def test_solar_journey():
    
    df_coefficient_data = loadExcelFile("coefficients.xlsx")
    data = get_and_set_data_from_quoteId()

    
    # Calculate consumption and assert with received data
    df_calculated_consumption = calculate_consumption(df_coefficient_data)
    verify_calculated_with_api(df_calculated_consumption["consumption"].sum(), "consumption")		
    verify_calculated_with_api_monthly(df_calculated_consumption, data, "consumption")
    
    # # Calculate generation and assert with received data
    df_calculated_generation = calculate_generation(df_coefficient_data)
    verify_calculated_with_api(df_calculated_generation["generation"].sum(), "generation")		
    verify_calculated_with_api_monthly(df_calculated_generation, data, "generation")
    
    # calculate battery capacity and assert with recieved data
    # df_calculated_batery_capacity = calculate_battery_capacity()
    
    df_results = get_unitRate_dataframe(data, "proposed", "import")
    logging.info(df_results.to_string)

    
    