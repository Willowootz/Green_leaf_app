from flask import Flask, request, render_template, jsonify
import pandas as pd
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

app = Flask(__name__)

#load model
#MAKE SURE FLASK SERVER IS RUNNING FIRST
df = pd.read_json('cleaned_dataset.json')
# Ensure categorical columns exist for dummy encoding
df_encoded = pd.get_dummies(df, columns=['Make', 'FuelType', 'Model'])
X = df_encoded.drop('CO2', axis=1)
y = df_encoded['CO2']

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)
X_train_cols = X.columns

#routing
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    car_info = {
        "Make": data['make'].upper(),
        "Model": data['model'].upper(),
        "EngineSize": float(data['engine_size']),
        "FuelType": data['fuel_type'].upper()
    }
    distance = float(data['distance'])

    #process info with dataframe
    df_car = pd.DataFrame([car_info])
    df_car = pd.get_dummies(df_car)
    
    missing_cols = [col for col in X_train_cols if col not in df_car.columns]
    if missing_cols:
        zeros = pd.DataFrame(0, index=df_car.index, columns=missing_cols)
        df_car = pd.concat([df_car, zeros], axis=1)
    
    df_car = df_car[X_train_cols]
    
    #final calculation
    co2_per_unit = model.predict(df_car)[0]
    total_emissions = (co2_per_unit * distance) / 1000
    
    return jsonify({'emissions': round(total_emissions, 3)})

if __name__ == '__main__':
    app.run(debug=True)