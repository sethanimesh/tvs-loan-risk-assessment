from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import joblib

model = joblib.load('Machine Learning/Demographic/demographic.pkl')

app = Flask(__name__)

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
    if request.method == "POST":
        # Get form data
        person_age = float(request.form.get("person_age"))
        person_income = float(request.form.get("person_income"))
        person_home_ownership = request.form.get("person_home_ownership")
        loan_amnt = float(request.form.get("loan_amnt"))
        loan_int_rate = float(request.form.get("loan_int_rate"))
        loan_percent_income = float(request.form.get("loan_percent_income"))
        cb_person_default_on_file = request.form.get("cb_person_default_on_file")
        
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

        prediction = model.predict([input_data])[0]

        # Redirect to the location page with the prediction
        return redirect(url_for('location', prediction=prediction))
    
    return render_template("index.html")

@app.route("/location")
def location():
    prediction = request.args.get('prediction')
    # Render the location page and pass the prediction to it
    return render_template("location.html", prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)