from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os
import pickle

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Used for session management

# Load the trained model
with open('fraud_detection_model4.pkl', 'rb') as f:
    model = pickle.load(f)

# Ensure the Excel file for user registration exists
if not os.path.exists('users.xlsx'):
    pd.DataFrame(columns=['Username', 'Password']).to_excel('users.xlsx', index=False)

# Route for home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Load existing users
        users = pd.read_excel('users.xlsx')

        # Check if the username already exists
        if username in users['Username'].values:
            return "User already exists. Please login."

        # Add new user to the Excel file
        new_user = pd.DataFrame({'Username': [username], 'Password': [password]})
        users = pd.concat([users, new_user], ignore_index=True)
        users.to_excel('users.xlsx', index=False)

        # Redirect to login after successful registration
        return redirect(url_for('login'))
    return render_template('register.html')

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Load existing users
        users = pd.read_excel('users.xlsx')

        # Validate credentials
        if username in users['Username'].values:
            if users.loc[users['Username'] == username, 'Password'].values[0] == password:
                session['username'] = username
                return redirect(url_for('input_page'))
            else:
                return "Incorrect password."
        else:
            return "User does not exist. Please register first."

    return render_template('login.html')

# Route for input page
@app.route('/input', methods=['GET', 'POST'])
def input_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Extract user inputs from the form
        input_columns = [
            'RenalDiseaseIndicator', 'ChronicCond_Alzheimer', 'ChronicCond_Heartfailure', 
            'ChronicCond_KidneyDisease', 'ChronicCond_Cancer', 'ChronicCond_ObstrPulmonary', 
            'ChronicCond_Depression', 'ChronicCond_Diabetes', 'ChronicCond_IschemicHeart', 
            'ChronicCond_Osteoporasis', 'ChronicCond_rheumatoidarthritis', 'ChronicCond_stroke', 
            'IPAnnualDeductibleAmt', 'OPAnnualDeductibleAmt'
        ]

        # Get the form input values, converting to float for prediction
        user_input = {col: float(request.form[col]) for col in input_columns}

        # Store user input in session for use on the result page
        session['user_input'] = user_input  

        # Redirect to the result page after input
        return redirect(url_for('result'))
    
    return render_template('input.html')

@app.route('/result')
def result():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Retrieve user input from session
    user_input = session.get('user_input', {})

    # List of input columns used during training
    input_columns = [
        'RenalDiseaseIndicator', 'ChronicCond_Alzheimer', 'ChronicCond_Heartfailure', 
        'ChronicCond_KidneyDisease', 'ChronicCond_Cancer', 'ChronicCond_ObstrPulmonary', 
        'ChronicCond_Depression', 'ChronicCond_Diabetes', 'ChronicCond_IschemicHeart', 
        'ChronicCond_Osteoporasis', 'ChronicCond_rheumatoidarthritis', 'ChronicCond_stroke', 
        'IPAnnualDeductibleAmt', 'OPAnnualDeductibleAmt'
    ]

    # Ensure the input dataframe matches the model's expected input format
    input_df = pd.DataFrame([user_input])

    # Reorder the columns of input_df to match the model's expected feature order
    input_df = input_df[input_columns]

    # Make prediction using the model
    prediction = model.predict(input_df)[0]

    # Determine result based on the prediction
    result = "Fraud" if prediction == 1 else "No Fraud"

    return render_template('result.html', result=result)

# Route for chart (example data)
@app.route('/chart')
def chart():
    # Example data to pass to the chart.html template
    accuracy = 0.9853
    confusion_matrix = [[1440, 0], [42, 1375]]
    
    return render_template('chart.html', accuracy=accuracy, confusion_matrix=confusion_matrix)

if __name__ == '__main__':
    app.run(debug=True)
