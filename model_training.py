import os
import pandas as pd
from utils import df_to_X_y
from dotenv import load_dotenv
from lstm_model import get_model
from sqlalchemy import create_engine
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

def train_test_split(X, y, test_size=0.15):
    val = int(X.shape[0] * test_size)
    train = X.shape[0] - (2 * val)
    val += train
    return X[:train], X[train:val], X[val:], y[:train], y[train:val], y[val:]

def train_model(model, X_train, X_val, y_train, y_val, epochs=15):
    es = EarlyStopping(monitor='val_loss', mode='min', patience=5)
    cp = ModelCheckpoint('model.keras', save_best_only=True, save_freq='epoch')
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=epochs, callbacks=[cp, es])


if __name__=='__main__':
    TRAIN = True
    TEST = True

    load_dotenv()
    api_key = os.getenv("API_KEY")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    print('Loading Data')
    connection_string = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(connection_string)
    query = 'SELECT * FROM air_quality'
    df = pd.read_sql(query, engine)
    if 'id' in df.columns:
        df = df.drop(columns=['id'])
    print('Data Successfully Loaded')

    window_size = 24
    X, y = df_to_X_y(df, window_size, TRAIN)
    X_train, X_val, X_test, y_train, y_val, y_test = train_test_split(X, y)

    if TRAIN:
        model = get_model(window_size)
        train_model(model, X_train, X_val, y_train, y_val, 30)
    if TEST:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model = load_model(os.path.join(base_dir, 'model.keras'))
        print('Evaluating Validation Set:')

        model.evaluate(X_val, y_val)
        print('Evaluating Test Set:')
        model.evaluate(X_test, y_test) 
        
        