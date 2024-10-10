import pandas as pd
import random
from datetime import datetime
import time
import os

def generate_data():
    now = datetime.now()
    temperature = random.uniform(20, 30)
    humidity = random.uniform(30, 60)
    occupancy = random.randint(0, 1)  
    energy_consumption = random.uniform(10, 50)  
    data = {
        'Timestamp': [now],
        'Temperature': [temperature],
        'Humidity': [humidity],
        'Occupancy': [occupancy],
        'EnergyConsumption': [energy_consumption]
    }

    df = pd.DataFrame(data)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

if __name__ == '__main__':
   
    if not os.path.isfile('building_data.csv'):
        df = generate_data()
        df.to_csv('building_data.csv', index=False)
    try:
        while True:
            df = generate_data()
            df.to_csv('building_data.csv', mode='a', header=False, index=False)
            print('Data appended to CSV file.')
            time.sleep(60)  
    except KeyboardInterrupt:
        print("Data simulation stopped.")

