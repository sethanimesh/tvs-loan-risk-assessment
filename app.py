from flask import Flask, render_template, request
import numpy as np
import joblib

# Load your trained demographic model
model = joblib.load('Machine Learning/Demographic/demographic.pkl')

app = Flask(__name__)

# Define mappings for categorical fields
home_ownership_mapping = {
    "own": 0,
    "rent": 1,
    "mortgage": 2
}

default_on_file_mapping = {
    "yes": 1,
    "no": 0
}

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    if request.method == "POST":
        # Get input data from the form and apply necessary conversions
        person_age = float(request.form.get("person_age"))
        person_income = float(request.form.get("person_income"))
        person_home_ownership = request.form.get("person_home_ownership")
        loan_amnt = float(request.form.get("loan_amnt"))
        loan_int_rate = float(request.form.get("loan_int_rate"))
        loan_percent_income = float(request.form.get("loan_percent_income"))
        cb_person_default_on_file = request.form.get("cb_person_default_on_file")
        
        # Convert categorical inputs to numeric using the defined mappings
        person_home_ownership_encoded = home_ownership_mapping.get(person_home_ownership, -1)
        cb_person_default_on_file_encoded = default_on_file_mapping.get(cb_person_default_on_file, -1)

        # Make sure all inputs are in the required format
        input_data = np.array([
            person_age,
            person_income,
            person_home_ownership_encoded,
            loan_amnt,
            loan_int_rate,
            loan_percent_income,
            cb_person_default_on_file_encoded
        ])

        # Use the model to predict
        prediction = model.predict([input_data])[0]
        
    return render_template("index.html", prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)