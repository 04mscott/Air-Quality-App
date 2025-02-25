import os
import mysql
import mysql.connector
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

db_connection = mysql.connector.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name
)

cursor = db_connection.cursor()
# cursor.execute("SHOW TABLES;")  # Test if the connection works
# for table in cursor:
#     print(table)
# cursor.execute("SELECT * FROM air_quality LIMIT 1")
# column_names = [desc[0] for desc in cursor.description]
# print(column_names)

# db_connection.close()

def get_air_quality():
    # Get locations
    headers = {"X-API-Key": api_key}
    url = 'https://api.openaq.org/v3/locations'
    params = {'limit' : 1}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        results = data['results']
        location_ids = []
        for r in results:
            location_ids.append(int(r['id']))
            print(location_ids)
    else:
        print(f"ERROR: {response.status_code}, {response.text}")
        return

    # Get sensors from location
    url = "https://api.openaq.org/v3/locations/{location_ids[0]}/sensors"
    params = {'locations_id' : location_ids[0]}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"ERROR: {response.status_code}, {response.text}")
        return

def save_air_quality(city, data):
    co = float(data["co"])
    no = float(data["no"])
    no2 = float(data["no2"])
    o3 = float(data["o3"])
    so2 = float(data['so2'])
    pm2_5 = float(data["pm2_5"])
    pm10 = float(data["pm10"])
    nh3 = float(data['nh3'])

    sql = "INSERT INTO air_quality (city, co, no, no2, o3, so2, pm2_5, pm10, nh3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (city, co, no, no2, o3, so2, pm2_5, pm10, nh3)
    cursor.execute(sql, values)
    db_connection.commit()


# st.title('Air Quality Tracker')
# city = st.text_input("Enter city name (e.g., New York, London):")

# if city:
#     data = get_air_quality(city)
#     if data:
#         st.json(data)
#     else:
#         st.error("City not found or API error")

if __name__=='__main__':
    data = get_air_quality()
    print(data)
