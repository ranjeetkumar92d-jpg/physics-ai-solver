import os
import io
import base64

from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY) if API_KEY else None

# Temporary notes storage
NOTES_TEXT = ""


@app.route("/")
def home():
    return "Physics Notes AI Backend is Working!"


# =========================================
# UPLOAD / BUILD NOTES
# =========================================

@app.route("/upload-notes", methods=["POST"])
def upload_notes():

    global NOTES_TEXT

    if client is None:
        return jsonify({
            "error": "GEMINI_API_KEY is not configured."
        }), 500

    pdf = request.files.get("pdf")

    if not pdf:
        return jsonify({
            "error": "PDF file is required."
        }), 400

    try:

        pdf_bytes = pdf.read()

        if not pdf_bytes:
            return jsonify({
                "error": "PDF is empty."
            }), 400

        # Send complete PDF to Gemini for extraction
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type="application/pdf"
                ),
                """
You are processing a Physics teaching-notes PDF.

Create a clean Physics knowledge base from this PDF.

IMPORTANT:

1. Preserve Physics formulas accurately.
2. Preserve definitions.
3. Preserve laws and principles.
4. Preserve important derivations.
5. Preserve examples.
6. Preserve numerical-solving methods.
7. Preserve chapter/topic names.
8. Preserve units.
9. Preserve symbols such as:
   α β γ θ λ μ ρ π ω
10. Preserve fractions, powers, roots,
    differentiation and integration.

Do NOT invent information.

Organize the extracted knowledge as:

CHAPTER
TOPIC
CONCEPT
FORMULAS
DEFINITIONS
IMPORTANT POINTS
SOLVING METHOD
EXAMPLES

Return only the structured Physics knowledge base.
"""
            ]
        )

        NOTES_TEXT = response.text

        return jsonify({
            "success": True,
            "message": "Physics notes processed successfully.",
            "characters": len(NOTES_TEXT)
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# SOLVE QUESTION USING NOTES
# =========================================

@app.route("/solve", methods=["POST"])
def solve():

    if client is None:
        return jsonify({
            "error": "GEMINI_API_KEY is not configured."
        }), 500

    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Question is required."
        }), 400

    if not NOTES_TEXT:

        return jsonify({
            "error": "Physics notes are not loaded yet. Please upload/build your notes first."
        }), 400

    try:

        prompt = f"""
You are a Physics AI tutor.

The student is asking:

{question}

Below is the student's own Physics notes.

================ NOTES ================
{NOTES_TEXT}
========================================

STRICT RULES:

1. Treat the supplied notes as the PRIMARY SOURCE.
2. Find the relevant chapter/topic/formula from the notes.
3. Base the solution on the notes.
4. Follow the terminology and method used in the notes when possible.
5. Do NOT silently replace the notes with generic knowledge.
6. If the required information is NOT present in the notes, clearly say:

"यह जानकारी दिए गए notes में नहीं मिली।"

7. You may use basic Physics reasoning to calculate or explain
   something that follows directly from a formula in the notes.
8. Do not invent formulas or facts.

Answer format:

### Chapter
### Topic
### Notes Concept
### Given
### Find
### Formula
### Solution
### Final Answer
### Simple Explanation

Use proper LaTeX for mathematics.

Example:

$$
v = u + at
$$

For fractions:

$$
v = \frac{{u+at}}{{1}}
$$

For powers:

$$
E = mc^2
$$

For roots:

$$
v = \sqrt{{2gh}}
$$
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return jsonify({
            "answer": response.text
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
