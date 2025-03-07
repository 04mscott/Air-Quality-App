import os
import time
import requests
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
from sqlalchemy import create_engine
from geopy.geocoders import Nominatim

# Load environment Variables
load_dotenv()
api_key = os.getenv("API_KEY")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Checks remaining storage in database, removes 10% of the oldest data if reaches 80% threshold
def check_storage():
    db_connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = db_connection.cursor()

    query = f"""
        SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS table_size_mb
        FROM information_schema.tables
        WHERE table_schema = '{db_name}'
        AND table_name = 'air_quality';
    """

    cursor.execute(query)
    result = cursor.fetchone()
    if result[0] < 16000:
        print(f'Table size: {result[0]} MB')
    else:
        print('Removing data to save space')
        query = '''
            DELETE FROM air_quality
            WHERE timestamp IN (
                SELECT timestamp FROM air_quality
                ORDER BY timestamp ASC
                LIMIT (SELECT COUNT(*) * 0.10 FROM air_quality)
            );
        '''
        cursor.execute(query)


# Return location Coordinates
def get_cords(city):
    geolocator = Nominatim(user_agent="geocoding_app")
    location = geolocator.geocode(city)
    if location:
        return location.latitude, location.longitude
    else:
        print("Location Error")
        return None

# Returns hourly historic for given location data between start and end time (UNIX Timestamp)
def get_historic_air_quality(city, start, end):
    cords = get_cords(city)
    if cords:
        lat, lon = cords
    else:
        return None
    url = f'http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start}&end={end}&appid={api_key}'
    response = requests.get(url).json()
    if 'list' in response:
        return response['list']
    else:
        print("API Request Error")
        print(response)
        return None

# Returns air quality data for given location from the past 5 hours in form of Pandas DataFrame
def get_current_air_quality(city, hours=24):
    data = {
        'city' : [],
        'time' : [],
        'co' : [],
        'no' : [], 
        'no2' : [], 
        'o3' : [], 
        'so2' : [], 
        'pm2_5' : [], 
        'pm10' : [], 
        'nh3' : []
    }
    end = int(time.time())
    start = end - (hours*60*60)
    response = get_historic_air_quality(city, start, end)
    if response:
        lst = response
        for l in lst:
            data['city'].append(city)
            data['time'].append(l['dt'])
            for key in l['components']:
                data[key].append(l['components'][key])
        df = pd.DataFrame(data)
        return df
    else:
        print("API Request Error")
        print(response)
        return None
    
# Given a dict, list of locations, start date, and end date, gets the historic air quality
# data for each location and adds it to data, converts data into pandas DataFrame, then adds
# the DataFrame to MySQL Database
def save_initial_training_data(data, cities, start, end):
    for city in cities:
        print(f'Fetching data for {city}...')
        response = get_historic_air_quality(city, start, end)
        if response:
            lst = response
            for l in lst:
                data['city'].append(city)
                data['time'].append(l['dt'])
                for key in l['components']:
                    data[key].append(l['components'][key])
    df = pd.DataFrame(data)
    df = df.sort_values(by=['time'])
    print(df.info)
    print(df.head(5))
    answer = input('Add to Database? [y/n]')
    if answer == 'y':
        connection_string = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        engine = create_engine(connection_string)
        df.to_sql('air_quality', con=engine, if_exists='append', index=False)
        print('Data inserted successfully')
    else:
        print('Data insertion aborted')

# Saves current air quality data for each of the given cities, converts to pandas DataFrame,
# and adds data to MySQL Database. Designed to be called once every hour by a locally scheduled function call
def save_current_data(data, cities):
    t = int(time.time())
    for city in cities:
        print(f'Fetching data for {city}')
        response = get_current_air_quality(city)
        if response:
            lst = response
            data['city'].append(city)
            data['time'].append(t)
            for key in lst:
                data[key].append(lst[key])
    df = pd.DataFrame(data)
    df = df.sort_values(by=['time'])
    print(df.info)
    print(df.head(5))
    answer = input('Add to Database? [y/n]')
    connection_string = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(connection_string)
    df.to_sql('air_quality', con=engine, if_exists='append', index=False)
    print('Data inserted successfully')

if __name__=='__main__':
    CURRENT = False
    HISTORIC = False
    DATASET = True
    SAVE_CURRENT = False
    STORAGE = False
    SCHEDULED = False

    cities = ['New Dheli', 'Beijing', 'Karachi', 'Lagos', 'Cairo', 'Dhaka', 'Los Angeles', 'Mexico City', 'Jakarta', 'Tokyo', 'Vancouver', 'Zurich']
    data = {
        'city' : [],
        'time' : [],
        'co' : [],
        'no' : [], 
        'no2' : [], 
        'o3' : [], 
        'so2' : [], 
        'pm2_5' : [], 
        'pm10' : [], 
        'nh3' : []
    }
    city = 'New York'

    if CURRENT:
        df = get_current_air_quality(city)
        print(df.head())
    if HISTORIC:
        start = 1672549200 # 00:00:00 01/01/2024
        end = 1735707600 # 00:00:00 01/01/2025
        response = get_historic_air_quality(city, start, end)
        if response:
            lst = response
            for l in lst:
                data['city'].append(city)
                data['time'].append(l['dt'])
                for key in l['components']:
                    data[key].append(l['components'][key])
            df = pd.DataFrame(data)
            print(df.head(5))
            print(df.info)
    if DATASET:
        end = int(time.time())
        start = end - (3 * 365 * 24 * 60 * 60)
        save_initial_training_data(data, cities, start, end)
    if SAVE_CURRENT:
        save_current_data(data, cities)
    if STORAGE:
        check_storage()
    if SCHEDULED:
        check_storage()
        save_current_data(data, cities)