from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import google.generativeai as genai
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import os
import re

# Configure the API key for Google Generative AI
api_key = "AIzaSyBRMh11gAThUvN0j4iZ7SRVY9wP-0Xe8vc"  # Replace with your actual API key
genai.configure(api_key=api_key)

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = '123456'

# Initialize the Google model
model = genai.GenerativeModel("gemini-1.5-flash")

# Setup SQLite database
def init_db():
    with sqlite3.connect("chat.db") as conn:
        cursor = conn.cursor()
        # Create chat history table if not exists
        cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user TEXT,
                            message TEXT,
                            response TEXT,
                            timestamp TEXT)''')
        # Create users table if not exists
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE,
                            password TEXT)''')
        conn.commit()

init_db()

# Function to generate a response based on user input
def generate_response(user_input):
    try:
        prompt = f"""
        Respond to the following input without using any asterisks (*) or other special characters for formatting. 
        Use clear, concise language and organize information with main points and supporting details.
        Format your response as follows:
        - Start with a brief definition or overview.
        - Use short paragraphs for main points.
        - Use single-line bullet points for lists or examples.

        User input: {user_input}
        """
        response = model.generate_content(prompt)
        if response:
            return format_response(response.text)
        else:
            return "Sorry, I couldn't generate a response."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to format the response into structured headings and bullet points
def format_response(response_text):
    clean_text = re.sub(r'\*+', '', response_text)
    
    sections = clean_text.split('\n\n')
    formatted = []

    for section in sections:
        if section.strip():
            lines = section.strip().split('\n')
            if len(lines) > 1:
                formatted.append(f"{lines[0].strip()}\n")
                for line in lines[1:]:
                    if line.strip():
                        formatted.append(f"- {line.strip()}\n")
            else:
                formatted.append(f"{section.strip()}\n")

    return ''.join(formatted)

# Function to save chat to the database
def save_chat(user, message, response):
    with sqlite3.connect("chat.db") as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''INSERT INTO chat_history (user, message, response, timestamp)
                          VALUES (?, ?, ?, ?)''', (user, message, response, timestamp))
        conn.commit()

# Function to get user by username from the database
def get_user_by_username(username):
    with sqlite3.connect("chat.db") as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return cursor.fetchone()

# Function to register a new user
def register_user(username, password):
    hashed_password = generate_password_hash(password)
    with sqlite3.connect("chat.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists

# Route: Home page (Chat Interface)
@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html', username=session['user'])  # Pass the username to the template
    return redirect(url_for('login'))

# Route: Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash(user[2], password):  # user[2] is the hashed password
            session['user'] = username
            return redirect(url_for('index'))
        return "Invalid credentials, please try again."
    return render_template('login.html')

# Route: Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if register_user(username, password):
            return redirect(url_for('login'))
        else:
            return "Username already exists. Please choose another one."
    return render_template('register.html')

# Route: Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Route: Chat API
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        bot_response = generate_response(user_message)

        if not bot_response:
            return jsonify({'error': 'Bot did not respond properly'}), 500

        save_chat(session['user'], user_message, bot_response)  # Save chat to database

        return jsonify({'response': bot_response})

    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

# Route: Chat history
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect("chat.db") as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT message, response, timestamp FROM chat_history WHERE user = ?', (session['user'],))
        history = cursor.fetchall()
    
    return render_template('history.html', history=history)

# Route: FAQ page
@app.route('/faq')
def faq():
    return render_template('faq.html')

# Main execution
if __name__ == '__main__':
    app.run(debug=True)
