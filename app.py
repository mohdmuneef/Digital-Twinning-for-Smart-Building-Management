from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import logging
import random
import joblib
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load or train machine learning model
def load_or_train_model(df):
    try:
        model = joblib.load('energy_model.pkl')
        logging.info("Model loaded successfully.")
    except:
        logging.info("Training new model.")
        X = df[['Temperature', 'Humidity', 'Occupancy']]
        y = df['EnergyConsumption']
        model = LinearRegression().fit(X, y)
        joblib.dump(model, 'energy_model.pkl')
        logging.info("Model trained and saved.")
    return model

# Function to generate simulated data
def generate_data():
    now = datetime.now()
    timestamps = [now - timedelta(hours=i) for i in range(24)]
    temperatures = [random.uniform(20, 30) for _ in range(24)]
    humidities = [random.uniform(30, 60) for _ in range(24)]
    occupancies = [random.randint(0, 1) for _ in range(24)]
    energy_consumptions = [random.uniform(10, 50) for _ in range(24)]

    data = {
        'Timestamp': timestamps,
        'Temperature': temperatures,
        'Humidity': humidities,
        'Occupancy': occupancies,
        'EnergyConsumption': energy_consumptions
    }

    df = pd.DataFrame(data)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

# Load simulated data
df = generate_data()
model = load_or_train_model(df)

# Predictive analytics
def predict_conditions(df, model):
    try:
        df = df.set_index('Timestamp')
        future_times = pd.date_range(start=df.index[-1], periods=25, freq='H')[1:]
        temperature_pred = df['Temperature'].rolling(window=3).mean().iloc[-1] + np.random.uniform(-1, 1, size=24)
        humidity_pred = df['Humidity'].rolling(window=3).mean().iloc[-1] + np.random.uniform(-1, 1, size=24)
        occupancy_pred = np.random.randint(0, 2, size=24)

        X_future = pd.DataFrame({
            'Temperature': temperature_pred,
            'Humidity': humidity_pred,
            'Occupancy': occupancy_pred
        })
        energy_pred = model.predict(X_future)

        future_df = pd.DataFrame({
            'Timestamp': future_times,
            'Temperature': temperature_pred,
            'Humidity': humidity_pred,
            'Occupancy': occupancy_pred,
            'EnergyConsumption': energy_pred
        })
        return future_df
    except Exception as e:
        logging.error(f"Error in predictive analytics: {e}")
        return pd.DataFrame()

@app.route('/', methods=['GET', 'POST'])
def index():
    global df, model
    custom_plot = request.form.get('plot_type', 'Temperature and Humidity')
    future_df = predict_conditions(df, model)

    if custom_plot == 'Energy Consumption':
        fig = px.line(df, x='Timestamp', y='EnergyConsumption', title='Energy Consumption')
        fig.update_xaxes(title='Time')
        fig.update_yaxes(title='Energy Consumption (kWh)')
        fig.add_trace(go.Scatter(x=future_df['Timestamp'], y=future_df['EnergyConsumption'], mode='lines', name='Predicted Energy Consumption'))
    else:
        fig = px.line(df, x='Timestamp', y=['Temperature', 'Humidity'], title='Building Conditions')
        fig.update_xaxes(title='Time')
        fig.update_yaxes(title='Value')
        fig.add_trace(go.Scatter(x=future_df['Timestamp'], y=future_df['Temperature'], mode='lines', name='Predicted Temperature'))
        fig.add_trace(go.Scatter(x=future_df['Timestamp'], y=future_df['Humidity'], mode='lines', name='Predicted Humidity'))

    plot_div = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template('index.html', plot_div=plot_div, custom_plot=custom_plot)

if __name__ == '__main__':
    app.run(debug=True)
    
