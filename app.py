from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_cors import CORS
import numpy as np
import joblib
import sqlite3
import json
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
import markdown
import re
import requests
import pandas as pd

model = joblib.load('Machine Learning/Demographic/demographic.pkl')

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'
CORS(app)

city_risk_df = pd.read_csv('Machine Learning/Location/city_wise_risk_data.csv')

home_ownership_mapping = {
    "own": 0,
    "rent": 1,
    "mortgage": 2
}

default_on_file_mapping = {
    "yes": 1,
    "no": 0
}

def get_location_risk_factor(city):
    min_risk_factor = city_risk_df['Credit_Risk'].min()
    max_risk_factor = city_risk_df['Credit_Risk'].max()

    risk_factor = city_risk_df.loc[city_risk_df['Towns'] == city, 'Credit_Risk']
    if not risk_factor.empty:
        risk_factor_value = float(risk_factor.values[0])
        normalized_risk_factor = (risk_factor_value - min_risk_factor) / (max_risk_factor - min_risk_factor)
        return normalized_risk_factor
    return 0  

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
                       risk_score REAL,
                       final_risk_score REAL,
                       FOREIGN KEY (user_id) REFERENCES predictions (id))''')
    
    cursor.execute("PRAGMA table_info(results)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'final_risk_score' not in columns:
        cursor.execute('ALTER TABLE results ADD COLUMN final_risk_score REAL')
        print("Added 'final_risk_score' column to 'results' table.")


    conn.commit()
    conn.close()

def store_prediction(data):
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO predictions 
                      (person_age, person_income, person_home_ownership, loan_amnt, loan_int_rate, loan_percent_income, cb_person_default_on_file, prediction, latitude, longitude, city)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def save_risk_score(user_id, risk_score):
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE results SET risk_score=? WHERE user_id=?', (risk_score, user_id))

    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            person_age = float(request.form.get("person_age"))
            person_income = float(request.form.get("person_income"))
            person_home_ownership = request.form.get("person_home_ownership")
            loan_amnt = float(request.form.get("loan_amnt"))
            loan_int_rate = float(request.form.get("loan_int_rate"))
            loan_percent_income = float(request.form.get("loan_percent_income"))
            cb_person_default_on_file = request.form.get("cb_person_default_on_file")
        except (TypeError, ValueError):
            return render_template("index.html", error="Invalid input data. Please ensure all fields are filled correctly.")

        person_home_ownership_encoded = home_ownership_mapping.get(person_home_ownership, -1)
        cb_person_default_on_file_encoded = default_on_file_mapping.get(cb_person_default_on_file, -1)

        input_data = np.array([
            person_age,
            person_income,
            person_home_ownership_encoded,
            loan_amnt,
            loan_int_rate,
            loan_percent_income,
            cb_person_default_on_file_encoded
        ])

        try:
            prediction = float(model.predict([input_data])[0])
        except Exception as e:
            return render_template("index.html", error=f"Prediction error: {str(e)}")

        data_to_store = (
            person_age,
            person_income,
            person_home_ownership,
            loan_amnt,
            loan_int_rate,
            loan_percent_income,
            cb_person_default_on_file,
            prediction,  
            0, 0, 0
        )

        user_id = store_prediction(data_to_store)
        session['user_id'] = user_id

        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO results (user_id, score, wrong, grade, risk_score)
                          VALUES (?, 0, 0, 0, 0)''', (user_id,))
        conn.commit()
        conn.close()

        return redirect(url_for('salary_analysis'))

    return render_template("index.html")

@app.route("/get_risk_factor", methods=["GET"])
def get_risk_factor():
    city = request.args.get('city')
    if city:
        risk_factor = get_location_risk_factor(city)
        return {"city": city, "risk_factor": risk_factor}
    return {"error": "City not provided"}, 400

@app.route("/location")
def location():
    return render_template("location.html")

@app.route("/store_location", methods=["POST"])
def store_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    city = data.get('city')

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID not found in session"}), 400

    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE predictions SET latitude=?, longitude=?, city=?
                      WHERE id = ?''', 
                   (latitude, longitude, city, user_id))
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

    user_id = session.get('user_id')
    if not user_id:
        return "User ID not found in session", 400

    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()

    cursor.execute('''UPDATE results SET score=?, wrong=?, grade=? WHERE user_id=?''', (score, wrong, grade, user_id))
    conn.commit()

    cursor.execute('''SELECT p.prediction, p.city, r.grade, r.risk_score
                      FROM predictions p
                      JOIN results r ON p.id = r.user_id
                      WHERE p.id = ?''', (user_id,))
    data = cursor.fetchone()

    if not data:
        return "User data not found", 404

    demographic_prediction, city, grade, risk_score = data

    location_risk_factor = get_location_risk_factor(city)
    normalized_risk_score = (risk_score - 1) / 9 

    final_risk_score = round(
        ((0.40 * (1-demographic_prediction)) +
         (0.25 * normalized_risk_score) +
         (0.20 * location_risk_factor) +
         (0.15 * (normalized_grade))) * 100,
        2
    )

    cursor.execute('''UPDATE results SET final_risk_score=? WHERE user_id=?''', (final_risk_score, user_id))
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
                             results.score, results.wrong, results.grade, results.risk_score
                      FROM predictions
                      JOIN results ON predictions.id = results.user_id''')
    rows = cursor.fetchall()

    conn.close()

    return render_template("view_results.html", rows=rows)

@app.route("/generate_analysis", methods=["POST"])
def generate_analysis():
    try:
        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT p.person_age, p.person_income, p.person_home_ownership, p.loan_amnt, 
                   p.loan_int_rate, p.loan_percent_income, p.cb_person_default_on_file, 
                   p.prediction, p.city, r.score, r.wrong, r.grade
            FROM predictions p
            LEFT JOIN results r ON p.id = r.user_id
            ORDER BY p.id DESC LIMIT 1
        ''')
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({"error": "No prediction data found."}), 404

        (person_age, person_income, person_home_ownership, loan_amnt, loan_int_rate,
         loan_percent_income, cb_person_default_on_file, prediction, city, score, wrong, grade) = row

        prompt_prefix = ("You are an expert in financial risk assessment. If the prediction is 1, it means the loan was rejected. "
                         "If the prediction is 0, it means the loan was accepted. Give your own view on why the application should be "
                         "rejected or accepted. Based on the following data, provide an analysis of factors that could impact a loan decision, "
                         "without giving any final decision:\n\n")
        prompt = f"""
        Age: {person_age} years
        Income: ₹{person_income}
        Home Ownership: {person_home_ownership}
        Loan Amount: ₹{loan_amnt}
        Interest Rate: {loan_int_rate}%
        Loan Percent of Income: {loan_percent_income}%
        Default on File: {cb_person_default_on_file}
        Prediction: {prediction}
        City: {city}
        Psychometric Score: {score}, Mistakes: {wrong}, Grade: {grade}
        
        If the final risk score is above 50%, then the loan will be given. In this only give the reasons for rejection and if the final risk score is below 50%, give reasons for acceptance  
        """

        data = request.get_json()
        model_name = data.get("model", "llama3.1")  
        stream = data.get("stream", False)

        ollama_url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": model_name,
            "prompt": prompt_prefix + prompt.strip(),
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
        generated_text = markdown.markdown(generated_text)
        return {"response": generated_text}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/show_analysis")
def show_analysis():
    try:
        generate_url = request.host_url.rstrip('/') + url_for('generate_analysis')
        
        payload = {
            'model': 'llama3.1', 
            'stream': False
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(generate_url, json=payload, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            analysis = response_data.get('response', 'No analysis provided')
        else:
            analysis = f"Error: Unable to fetch analysis, Status Code: {response.status_code}"

        return render_template('analysis.html', analysis=analysis)

    except Exception as e:
        return f"Error: {str(e)}", 500

def generate(user_document_base64):
    vertexai.init(project="optimum-pier-437602-t7", location="us-central1")
    model = GenerativeModel("gemini-1.5-flash-002")
    
    document1 = Part.from_data(
        mime_type="application/pdf",
        data=base64.b64decode(user_document_base64),
    )

    text1 = """Analyze the customer's income and expense data over the last 6 months to assess their financial risk for loan approval. Provide the output in the 
    Risk Score: <Risk Score>
    Analysis: <Analysis> (In points in each line)

The "risk_score" should be a value between 1 and 10, where 1 indicates low risk and 10 indicates high risk. The "analysis" should be a concise explanation of why this score was assigned based on the provided financial data."""
    
    safety_settings = [
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
    ]

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 1,
        "top_p": 0.95,
    }

    responses = model.generate_content(
        [text1, document1],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    generated_text = ""
    for response in responses:
        generated_text += response.text
    return generated_text

@app.route('/salary_analysis')
def salary_analysis():
    return render_template('salary.html')

@app.route('/generate-risk-score', methods=['POST'])
def generate_risk_score():
    if 'pdf_file' not in request.files:
        return render_template('salary.html', error="No file part")
    
    pdf_file = request.files['pdf_file']
    
    if pdf_file.filename == '':
        return render_template('salary.html', error="No selected file")
    
    pdf_data = pdf_file.read()
    
    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
    
    result = generate(pdf_base64)
    risk_score_match = re.search(r"Risk Score:\s*(\d+)", result)
    if risk_score_match:
        risk_score = int(risk_score_match.group(1))
    else:
        return render_template('salary.html', error="Risk Score not found in the analysis")
    
    user_id = session.get('user_id')
    if not user_id:
        return render_template('salary.html', error="User ID not found in session")
    
    save_risk_score(user_id, risk_score)
    
    return render_template('salary.html', result=result)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)