from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from dotenv import load_dotenv
import requests
import json

app = Flask(__name__)
load_dotenv()

df = pd.read_csv('data.csv')
API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

@app.route('/')
def index():
    categories = df['category'].unique()
    return render_template('index.html', categories=categories)

@app.route('/get_products', methods=['POST'])
def get_products():
    category = request.json['category']
    products = df[df['category'] == category]['product_name'].tolist()
    return jsonify(products)

@app.route('/generate_reviews', methods=['POST'])
def generate_reviews():
    product = request.json['product']
    category = df[df['product_name'] == product]['category'].values[0]

    prompt = f"""
You are an expert product reviewer who writes detailed, engaging, and human-like reviews.

Your task is to generate 5 unique, realistic, and natural-sounding customer reviews for the following product:

Product: {product}
Category: {category}

Guidelines:
- Each review must be 2–4 sentences long.
- Each review should sound like it’s written by a real person with a genuine experience.
- Use a mix of informal and natural language, just like you'd find in Amazon or Flipkart reviews.
- Include different tones (e.g., happy, impressed, minor complaints, satisfied, neutral).
- Do NOT repeat the same wording or structure.
- Avoid promotional or robotic language.
- Do not mention anything about being an AI or generating text.

Output format:
- Review 1: ...
- Review 2: ...
- Review 3: ...
- Review 4: ...
- Review 5: ...
"""

    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()

        # Extract text response
        text_output = data['candidates'][0]['content']['parts'][0]['text']

        # Optional: print raw output
        print("Gemini Raw Output:\n", text_output)

        # Parse reviews
        reviews = []
        for line in text_output.strip().split("\n"):
            line = line.strip("-• ").strip()
            if line.lower().startswith("review"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    reviews.append(parts[1].strip())

        return jsonify(reviews[:5])

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
