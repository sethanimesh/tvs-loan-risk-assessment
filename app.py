from flask import Flask, render_template, request, redirect, url_for, jsonify
import numpy as np
import joblib
import sqlite3
import json

import requests

model = joblib.load('Machine Learning/Demographic/demographic.pkl')

app = Flask(__name__)

import pandas as pd

city_risk_df = pd.read_csv('Machine Learning/Location/city_wise_risk_data.csv')

def get_location_risk_factor(city):
    min_risk_factor = city_risk_df['Credit_Risk'].min()
    max_risk_factor = city_risk_df['Credit_Risk'].max()

    risk_factor = city_risk_df.loc[city_risk_df['Towns'] == city, 'Credit_Risk']
    if not risk_factor.empty:
        risk_factor_value = float(risk_factor.values[0])
        normalized_risk_factor = (risk_factor_value - min_risk_factor) / (max_risk_factor - min_risk_factor)
        return normalized_risk_factor
    return 0  

home_ownership_mapping = {
    "own": 0,
    "rent": 1,
    "mortgage": 2
}

default_on_file_mapping = {
    "yes": 1,
    "no": 0
}

def init_db():
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS predictions
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       person_age REAL,
                       person_income REAL,
                       person_home_ownership TEXT,
                       loan_amnt REAL,
                       loan_int_rate REAL,
                       loan_percent_income REAL,
                       cb_person_default_on_file TEXT,
                       prediction REAL,
                       latitude REAL,
                       longitude REAL,
                       city TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS results
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER,
                       score INTEGER,
                       wrong INTEGER,
                       grade REAL,
                       FOREIGN KEY (user_id) REFERENCES predictions (id))''')

    conn.commit()
    conn.close()

def store_prediction(data):
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO predictions 
                      (person_age, person_income, person_home_ownership, loan_amnt, loan_int_rate, loan_percent_income, cb_person_default_on_file, prediction, latitude, longitude, city)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Retrieve form data and convert to appropriate types
        person_age = float(request.form.get("person_age"))
        person_income = float(request.form.get("person_income"))
        person_home_ownership = request.form.get("person_home_ownership")
        loan_amnt = float(request.form.get("loan_amnt"))
        loan_int_rate = float(request.form.get("loan_int_rate"))
        loan_percent_income = float(request.form.get("loan_percent_income"))
        cb_person_default_on_file = request.form.get("cb_person_default_on_file")

        # Encoding categorical values
        person_home_ownership_encoded = home_ownership_mapping.get(person_home_ownership, -1)
        cb_person_default_on_file_encoded = default_on_file_mapping.get(cb_person_default_on_file, -1)

        # Prepare input data for the model
        input_data = np.array([
            person_age,
            person_income,
            person_home_ownership_encoded,
            loan_amnt,
            loan_int_rate,
            loan_percent_income,
            cb_person_default_on_file_encoded
        ])

        # Get prediction and cast it to a float
        prediction = float(model.predict([input_data])[0])

        # Prepare data to store, ensuring prediction is a float
        data_to_store = (
            person_age,
            person_income,
            person_home_ownership,
            loan_amnt,
            loan_int_rate,
            loan_percent_income,
            cb_person_default_on_file,
            prediction,  # Ensure prediction is stored as a float
            0, 0, 0
        )

        # Store the prediction in the database or file
        store_prediction(data_to_store)

        # Redirect to the location route with the prediction
        return redirect(url_for('location', prediction=prediction))

    return render_template("index.html")

@app.route("/location")
def location():
    prediction = request.args.get('prediction')
    return render_template("location.html", prediction=prediction)

@app.route("/store_location", methods=["POST"])
def store_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    city = data.get('city')

    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE predictions SET latitude=?, longitude=?, city=?
                      WHERE id = (SELECT MAX(id) FROM predictions)''', 
                   (latitude, longitude, city))
    conn.commit()
    conn.close()

    return jsonify({"message": "Location stored successfully"})

@app.route("/psychometric")
def psychometric():
    return render_template("psychometric.html")

@app.route("/result")
def result():
    score = request.args.get('score', 0, type=int)
    wrong = request.args.get('wrong', 0, type=int)
    grade = request.args.get('grade', 0, type=float)

    min_grade = 0
    max_grade = 100
    normalized_grade = (grade - min_grade) / (max_grade - min_grade)

    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()

    # Get the most recent user data
    cursor.execute("SELECT id, prediction, city FROM predictions ORDER BY id DESC LIMIT 1")
    user_data = cursor.fetchone()
    user_id, demographic_prediction, city = user_data

    # Retrieve location risk factor (L) from the city_wise_risk_factor.csv file
    location_risk_factor = get_location_risk_factor(city)

    # Calculate the final risk score using the given weights
    final_risk_score = ((0.60 * demographic_prediction) + (0.20 * location_risk_factor) + (0.20 * normalized_grade))*100

    # Store results in the database
    cursor.execute('''INSERT INTO results (user_id, score, wrong, grade)
                      VALUES (?, ?, ?, ?)''', (user_id, score, wrong, grade))
    
    conn.commit()
    conn.close()

    return render_template("result.html", score=score, wrong=wrong, grade=grade, final_risk_score=final_risk_score)

@app.route("/view_predictions")
def view_predictions():
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM predictions")
    rows = cursor.fetchall()

    conn.close()

    return render_template("view_predictions.html", rows=rows)

@app.route("/view_results")
def view_results():
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT predictions.id, predictions.person_age, predictions.person_income, predictions.person_home_ownership, predictions.loan_amnt, predictions.loan_int_rate, 
                             predictions.loan_percent_income, predictions.cb_person_default_on_file, predictions.prediction, predictions.city,
                             results.score, results.wrong, results.grade
                      FROM predictions
                      JOIN results ON predictions.id = results.user_id''')
    rows = cursor.fetchall()

    conn.close()

    return render_template("view_results.html", rows=rows)


@app.route("/api/generate", methods=["POST"])
def generate_analysis():
    try:
        data = request.get_json()
        model_name = data.get("model", "llama3.1") 
        prompt = data.get("prompt", "Hello, How are you?")
        stream = data.get("stream", False)

        ollama_url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": stream
        }
        
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(ollama_url, headers=headers, json=payload)

        if stream:
            def generate():
                for line in response.iter_lines():
                    if line:
                        yield line.decode('utf-8') + "\n"
            return app.response_class(generate(), mimetype='text/plain')

        response_json = response.json()
        generated_text = response_json.get("response", "") 

        return generated_text

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    init_db()
    app.run(debug=True)