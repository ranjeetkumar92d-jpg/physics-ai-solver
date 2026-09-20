import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

# Gemini client
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    client = None
else:
    client = genai.Client(api_key=api_key)


@app.route("/")
def home():
    return "Physics AI Solver Backend is Working!"


@app.route("/solve", methods=["POST"])
def solve():

    if client is None:
        return jsonify({
            "error": "Gemini API key is not configured."
        }), 500

    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Question is required."
        }), 400

    prompt = f"""
You are a Physics teacher.

Solve the following Physics question clearly and step-by-step.

Question:
{question}

Rules:
1. Identify the given quantities.
2. Write the relevant Physics formula.
3. Substitute the values.
4. Show calculations.
5. Give the final answer with correct unit.
6. Keep the explanation easy for Class 11-12 / JEE-NEET students.
7. Do not invent information that is not given.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        answer = response.text

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
