import logging
from solar.methods.state_manager import StateManager

def set_data_from_quoteid_response(response):
    data = response.json()
    StateManager.set_value("_electricityConsumption",data["request"]["electricity"]["consumption"] )
    StateManager.set_value("_noOfPanel",data["request"]["solar"]["numberOfPanels"] )
    StateManager.set_value("_panelSizeKWH",data["request"]["solar"]["panelSize"] )
    StateManager.set_value("_panelIrradiance",data["request"]["performance"]["irradiance"] )
    StateManager.set_value("_solarDegradationFirst",data["request"]["solar"]["solarDegradationFirst"] )
    StateManager.set_value("_solarDegradationNext",data["request"]["solar"]["solarDegradationNext"] )
    StateManager.set_value("_solarGeneration",data["calculatedResults"][0]["electricity"]["solarGeneration"] )
    StateManager.set_value("_houseHoldConsumption",data["calculatedResults"][0]["electricity"]["householdConsumption"] )
    StateManager.set_value("_batteryUsagePct",data["request"]["solar"]["batteryUsagePct"])
    StateManager.set_value("_batteryDegradation",data["request"]["solar"]["batteryDegradation"])
    StateManager.set_value("_batterySize",data["request"]["solar"]["batterySize"])    
