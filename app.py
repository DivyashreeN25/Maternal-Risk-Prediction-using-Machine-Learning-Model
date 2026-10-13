from flask import Flask, render_template, request, session, redirect, url_for
import numpy as np
import joblib
import hashlib

# Load the Random Forest model
model = joblib.load('model.pkl')

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Simple user database
users = {
    'admin': hashlib.sha256('admin123'.encode()).hexdigest(),
    'doctor': hashlib.sha256('doctor123'.encode()).hexdigest(),
    'nurse': hashlib.sha256('nurse123'.encode()).hexdigest()
}

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if username in users and users[username] == hashed_password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password!')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match!')
        
        if username in users:
            return render_template('register.html', error='Username already exists!')
        
        if len(password) < 4:
            return render_template('register.html', error='Password must be at least 4 characters!')
        
        # Add new user
        users[username] = hashlib.sha256(password.encode()).hexdigest()
        return render_template('login.html', message='Registration successful! Please login.')
    
    return render_template('register.html')

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get values from the form
        age = float(request.form['age'])
        systolic_bp = float(request.form['systolic_bp'])
        diastolic_bp = float(request.form['diastolic_bp'])
        bs = float(request.form['bs'])
        body_temp = float(request.form['body_temp'])
        heart_rate = float(request.form['heart_rate'])
        
        # Prepare the test data
        test_data = np.array([[age, systolic_bp, diastolic_bp, bs, body_temp, heart_rate]])
        
        # Make prediction
        pred = model.predict(test_data)
        
        # Convert prediction to risk level
        risk_mapping = {0: 'low risk', 1: 'mid risk', 2: 'high risk'}
        risk_level = risk_mapping[pred[0]]
        
        return render_template('index.html', risk_level=risk_level, username=session['username'])
    
    except Exception as e:
        return render_template('index.html', error=str(e), username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)