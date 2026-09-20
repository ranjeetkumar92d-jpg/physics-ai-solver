import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from google import genai
from google.genai import types


app = Flask(__name__)
CORS(app)


# =========================================
# GEMINI
# =========================================

API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY) if API_KEY else None


# =========================================
# TEMPORARY PHYSICS NOTES
# =========================================

NOTES_TEXT = ""


# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return "Physics Notes AI Backend is Working!"


# =========================================
# UPLOAD PHYSICS NOTES
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

10. Preserve:
fractions
powers
roots
differentiation
integration
vectors
trigonometry

Do NOT invent information.

Organize the knowledge as:

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

            "message":
            "Physics notes processed successfully.",

            "characters":
            len(NOTES_TEXT)

        })


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# SOLVE PHYSICS QUESTION
# TEXT + IMAGE
# =========================================

@app.route("/solve", methods=["POST"])
def solve():

    if client is None:

        return jsonify({
            "error": "GEMINI_API_KEY is not configured."
        }), 500


    # -------------------------------------
    # GET QUESTION
    # -------------------------------------

    question = request.form.get(
        "question",
        ""
    ).strip()


    # -------------------------------------
    # GET IMAGE
    # -------------------------------------

    image = request.files.get("image")


    # -------------------------------------
    # CHECK QUESTION / IMAGE
    # -------------------------------------

    if not question and not image:

        return jsonify({
            "error":
            "Please enter a question or upload an image."
        }), 400


    # -------------------------------------
    # CHECK NOTES
    # -------------------------------------

    if not NOTES_TEXT:

        return jsonify({

            "error":
            "Physics notes are not loaded yet. "
            "Please upload/build your notes first."

        }), 400


    try:

        # =================================
        # BASE PROMPT
        # =================================

        prompt = f"""
You are a Physics AI tutor.

The student has provided a Physics question.

Student text question:

{question if question else "No text question. Read the uploaded image."}


Below is the student's own Physics notes.

================ NOTES ================

{NOTES_TEXT}

========================================


STRICT RULES:

1. Treat the supplied Physics notes as the PRIMARY SOURCE.

2. Find the relevant chapter, topic, concept and formula
   from the notes.

3. Base the solution on the notes whenever the required
   information is available.

4. Follow the terminology and method used in the notes
   whenever possible.

5. If the question is provided as an image, carefully read
   the image including mathematical symbols, numbers,
   diagrams and handwritten text.

6. Do NOT invent formulas or facts.

7. If the required information is NOT present in the notes,
   clearly say:

"यह जानकारी दिए गए notes में नहीं मिली।"

8. You may perform calculations using formulas found
   in the notes.

9. Explain the solution step-by-step.

10. Use proper LaTeX for mathematics.

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


Use LaTeX like:

$$
v = u + at
$$

$$
F = ma
$$

$$
E = mc^2
$$

$$
v = \\sqrt{{2gh}}
$$

For fractions:

$$
v = \\frac{{u+at}}{{1}}
$$
"""


        # =================================
        # GEMINI CONTENT
        # =================================

        contents = []


        # Add image first if available

        if image:

            image_bytes = image.read()

            if not image_bytes:

                return jsonify({
                    "error": "Uploaded image is empty."
                }), 400


            mime_type = image.mimetype or "image/jpeg"


            contents.append(

                types.Part.from_bytes(

                    data=image_bytes,

                    mime_type=mime_type

                )

            )


        # Add text prompt

        contents.append(prompt)


        # =================================
        # GEMINI
        # =================================

        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=contents

        )


        # =================================
        # RETURN ANSWER
        # =================================

        return jsonify({

            "answer": response.text

        })


    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500


# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )


    app.run(

        host="0.0.0.0",

        port=port

    )
