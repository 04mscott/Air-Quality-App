import os
import joblib
import numpy as np
import pandas as pd
from utils import df_to_X, graph_dataframe
from tensorflow.keras.models import load_model
from location_data import get_current_air_quality

cities = ['New Dheli', 'Beijing', 'Karachi', 'Lagos', 'Cairo', 'Dhaka', 'Los Angeles', 'Mexico City', 'Jakarta', 'Tokyo', 'Vancouver', 'Zurich']
base_dir = os.path.dirname(os.path.abspath(__file__))

def predict(x):
    print('Loading Keras Model...')
    model_path = os.path.join(base_dir, 'model.keras')
    model = load_model(model_path)
    print("Model Successfully Loaded")

    prediction = model.predict(x)

    scaler_path = os.path.join(base_dir, 'scaler.pkl')
    # print(scaler_path)
    scaler = joblib.load(scaler_path)
    prediction_scaled = scaler.inverse_transform(prediction)
    return prediction_scaled

def predict_n(df, n):
    for i in range(n):
        X = df_to_X(df.iloc[i:])
        prediction = predict(X)
        row = [df['city'].iloc[1]] + [int(df['time'].max()) + 3600] + list(prediction[0])
        tmp = pd.DataFrame([row], columns=df.columns)
        df = pd.concat([df, tmp])
        df = df.reset_index(drop=True)
    # print(df)
    return df


if __name__=='__main__':
    city = 'College Park' # input('Enter City Name: ')
    hours = 24 # input('How many hours do you want to predict? ')
    df = get_current_air_quality(city, 24)
    curr_time = int(df['time'].max()) + 3600
    X = df_to_X(df)
    #print(df)
    prediction = predict_n(df, int(hours))
    graph_dataframe(prediction)
    #print(f'Prediction: {prediction}')
    

