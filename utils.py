import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from location_data import get_current_air_quality
import plotly.express as px
import os
import joblib

base_dir = os.path.dirname(os.path.abspath(__file__))
cities = ['New Dheli', 'Beijing', 'Karachi', 'Lagos', 'Cairo', 'Dhaka',
          'Los Angeles', 'Mexico City', 'Jakarta', 'Tokyo', 'Vancouver', 'Zurich']
pollutants = ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']
colors = {'co' : '#eb4034', 'no' : '#e68439', 'no2' : '#e8c433', 'o3' : '#a6e32b',
          'so2' : '#14e07a', 'pm2_5' : '#1bc3e0', 'pm10' : '#2154de', 'nh3' : '#a827db'}

def preprocess(df, TRAIN, print_updates=False):
    df_clean = df.dropna()
    df_clean = df_clean.loc[(df_clean[pollutants] >= 0.0).all(axis=1)]
    df_clean = df_clean.sort_values(by='time')

    df_clean['time'] = pd.to_datetime(df_clean['time'], unit='s')
    df_clean['hour'] = df_clean['time'].dt.hour
    df_clean['hour_sin'] = np.sin((2 * np.pi * df_clean['hour']) / 24)
    df_clean['hour_cos'] = np.cos((2 * np.pi * df_clean['hour']) / 24)
    df_clean = df_clean.drop(columns=['time', 'hour'])

    df_clean = df_clean.reset_index(drop=True)
    if print_updates:
        print(df_clean.head(3))

    if TRAIN:
        scaler = StandardScaler()
        df_clean[pollutants] = scaler.fit_transform(df_clean[pollutants])
        joblib.dump(scaler, 'scaler.pkl')
    else:
        scaler = joblib.load(os.path.join(base_dir, 'scaler.pkl'))
        df_clean[pollutants] = scaler.transform(df_clean[pollutants])

    return df_clean


def df_to_X_y(df, window_size, TRAIN=True, print_updates=False):
    df_clean = preprocess(df, TRAIN, print_updates)
    df_np = df_clean.to_numpy()

    X = []
    y = []
    
    unique_cities = df_clean['city'].unique()
    if print_updates:
        print(f'Unique Cities: {unique_cities}')
        print('Converting Cities')

    for city in unique_cities:
        city_indices = df_clean.index[df_clean['city'] == city].to_list()
        for i in range(len(city_indices) - window_size):
            window = []
            for j in range(window_size):
                window.append(df_np[city_indices[i+j], 1:11])
            X.append(window)
            y.append(df_np[city_indices[i+window_size], 1:9])
        if print_updates:
            print(f'{city} X: {X}')
            print(f'{city} y: {y}')

    X = np.array(X).astype(float)
    y = np.array(y).astype(float)
    if print_updates:
        print(f'X: {X.shape}')
        print(X.dtype)
        print(f'y: {y.shape}')
        print(y.dtype)
    return X, y

def df_to_X(df, print_updates=False):
    df_clean = preprocess(df, True, print_updates)
    df_np = df_clean.to_numpy()

    X = []

    window = []
    for j in range(len(df_np)):
        window.append(df_np[j, 1:11])

    X.append(window)        
    X = np.array(X).astype(float)
        
    return X


def graph_dataframe(df):
    df = df.reset_index()
    time = pd.to_datetime(df['time'].iloc[-25])

    fig = px.line(
        df,
        x='time',
        y=pollutants
    )

    fig.add_vline(x=time)
    fig.add_vrect(x0=time, x1=df[pollutants].max().max())

    fig.update()

    fig.show()
    return fig


if __name__=='__main__':
    TRAIN = False
    PRED = False
    GRAPH = True
    hours = 24
    window_size = 2
    df = get_current_air_quality('Los Angeles', hours=hours)
    print(df)
    #df2 = get_current_air_quality('New York', hours=3)
    #df = pd.concat([df1, df2])
    #print(df)
    if TRAIN:
        df_to_X_y(df, window_size, True)
    if PRED:
        df_to_X(df, True)
    if GRAPH:
        time = int(df['time'].max()) - 43200
        graph_dataframe(df)

    