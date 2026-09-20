import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("GEMINI_API_KEY")

client = None

if API_KEY:
    client = genai.Client(api_key=API_KEY)


@app.route("/")
def home():
    return "Universal Physics AI Solver is Working!"


@app.route("/solve", methods=["POST"])
def solve():

    if client is None:
        return jsonify({
            "error": "GEMINI_API_KEY is not configured in Render."
        }), 500

    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Question is required."
        }), 400

    prompt = f"""
You are an expert Physics teacher.

You can solve Physics questions from:

Class 9
Class 10
Class 11
Class 12
JEE Main
JEE Advanced
NEET

The student can ask a question from ANY Physics chapter.

Do NOT assume a fixed chapter.

First automatically identify:

1. Chapter
2. Topic
3. Physics concept

Then solve the question.

IMPORTANT TEACHING STYLE:

- Explain in simple student-friendly language.
- Avoid unnecessarily difficult English.
- Do not skip important steps.
- Do not invent missing information.
- If information is missing, clearly say what is missing.
- Always check units.
- Check the final answer.
- For numerical questions, show calculations step-by-step.
- For conceptual questions, explain the concept with a simple example when useful.

Use this structure when applicable:

### Chapter
### Topic
### Given
### Find
### Concept
### Formula
### Solution
### Final Answer
### Simple Explanation

MATHEMATICS:

Use LaTeX for mathematical expressions.

Inline example:
$v = u + at$

Display equation example:

$$
v = u + at
$$

Use proper LaTeX for:

Fractions:
$$
v = \\frac{{u+at}}{{1}}
$$

Powers:
$$
E = mc^2
$$

Square roots:
$$
v = \\sqrt{{2gh}}
$$

Trigonometry:
$$
F_x = F\\cos\\theta
$$

Vectors:
$$
\\vec F = m\\vec a
$$

Differentiation:
$$
v = \\frac{{dx}}{{dt}}
$$

Integration:
$$
x = \\int v\\,dt
$$

GRAPHS:

If a graph is important for understanding the question:

- Explain what should be on the x-axis.
- Explain what should be on the y-axis.
- Explain the shape of the graph.
- Give the mathematical relation represented by the graph.

Do not invent experimental data.

The student question is:

{question}
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
