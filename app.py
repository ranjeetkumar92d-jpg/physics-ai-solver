import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

# Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY")

client = None

if API_KEY:
    client = genai.Client(api_key=API_KEY)


@app.route("/")
def home():
    return "Physics AI Solver Backend is Working!"


@app.route("/solve", methods=["POST"])
def solve():

    # Check API key
    if client is None:
        return jsonify({
            "error": "GEMINI_API_KEY is not configured in Render."
        }), 500

    # Read request
    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Question is required."
        }), 400

    # Physics teacher prompt
    prompt = f"""
You are an expert Physics teacher for Class 11, Class 12,
JEE Main, JEE Advanced and NEET students.

Solve the following Physics question accurately.

QUESTION:
{question}

Follow these rules:

1. First identify the given quantities.
2. Identify what has to be found.
3. Select the correct Physics concept.
4. Write the correct formula.
5. Substitute the values clearly.
6. Show calculations step-by-step.
7. Keep units throughout the calculation.
8. Check the final answer and unit.
9. Explain the concept briefly and clearly.
10. Never invent missing values.
11. If the question is ambiguous, clearly state what information is missing.
12. Use LaTeX for mathematical expressions.

Use LaTeX like:

$v = u + at$

For displayed equations use:

$$
v = u + at
$$

Make the solution easy to understand for a student.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
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

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
