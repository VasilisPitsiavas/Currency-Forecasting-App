import pandas as pd
import json
from datetime import datetime

def load_and_process_data(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    df = pd.DataFrame(data)
    
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    df = df[['time', 'open', 'high', 'low', 'close', 'volumefrom', 'volumeto']]
    
    return df

def save_to_csv(df, output_filename):
    """
    Saves the entire DataFrame to a CSV file.
   
    """
    df.to_csv(output_filename, index=False)  
    print(f"Data saved to {output_filename}")