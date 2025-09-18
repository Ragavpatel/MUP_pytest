import pandas as pd
import os

def loadExcelFile(filename):
    return pd.read_excel(os.getcwd()+"\solar\\testData\\"+filename, sheet_name=None)
    
