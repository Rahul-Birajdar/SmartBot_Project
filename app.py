from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
import re

# Configure the API key for Google Generative AI
api_key = "AIzaSyBRMh11gAThUvN0j4iZ7SRVY9wP-0Xe8vc"
genai.configure(api_key=api_key)

# Initialize the Flask app
app = Flask(__name__)

# Initialize the Google model
model = genai.GenerativeModel("gemini-1.5-flash")

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
            return "<p>Sorry, I couldn't generate a response.</p>"
    except Exception as e:
        return f"<p>An error occurred: {str(e)}</p>"
# Function to format the response into structured headings and bullet points

def format_response(response_text):
    # Remove all asterisks
    clean_text = re.sub(r'\*+', '', response_text)
    
    sections = clean_text.split('\n\n')
    formatted = []

    for section in sections:
        if section.strip():
            lines = section.split('\n')
            if len(lines) > 1:
                # Use the first line as a bold main point
                formatted.append(f"<p><strong>{lines[0].strip()}</strong></p>")
                formatted.append('<ul>')
                for line in lines[1:]:
                    if line.strip():
                        formatted.append(f"<li>{line.strip()}</li>")
                formatted.append('</ul>')
            else:
                # If it's a single line, add it as a paragraph
                formatted.append(f"<p>{section.strip()}</p>")

    return ''.join(formatted)

# Define the home route
@app.route('/')
def index():
    return render_template('index.html')

# Define the chatbot API route
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    bot_response = generate_response(user_input)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
