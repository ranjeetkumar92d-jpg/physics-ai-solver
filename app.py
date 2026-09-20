import os
import json
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
# NOTES FILE
# =========================================

NOTES_FILE = "physics_notes.txt"


def load_notes():

    if not os.path.exists(NOTES_FILE):
        return ""

    try:
        with open(
            NOTES_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read()

    except Exception:
        return ""


def save_notes(text):

    with open(
        NOTES_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(text)


# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return "Physics Notes AI Backend is Working!"


# =========================================
# UPLOAD NOTES
# =========================================

@app.route("/upload-notes", methods=["POST"])
def upload_notes():

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
4. Preserve derivations.
5. Preserve examples.
6. Preserve numerical solving methods.
7. Preserve chapter and topic names.
8. Preserve units.
9. Preserve Physics symbols.
10. Preserve fractions, powers, roots,
differentiation, integration, vectors and
trigonometry.

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


        notes = response.text


        if not notes:

            return jsonify({
                "error": "Gemini returned empty notes."
            }), 500


        # SAVE NOTES
        save_notes(notes)


        return jsonify({

            "success": True,

            "message":
            "Physics notes processed and saved successfully.",

            "characters":
            len(notes)

        })


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# CHECK NOTES
# =========================================

@app.route("/notes-status", methods=["GET"])
def notes_status():

    notes = load_notes()


    if not notes:

        return jsonify({

            "loaded": False,

            "message":
            "Physics notes are not loaded."

        })


    return jsonify({

        "loaded": True,

        "characters":
        len(notes),

        "message":
        "Physics notes are available."

    })


# =========================================
# SOLVE QUESTION
# =========================================

@app.route("/solve", methods=["POST"])
def solve():

    if client is None:

        return jsonify({
            "error": "GEMINI_API_KEY is not configured."
        }), 500


    # =====================================
    # READ NOTES FROM STORAGE
    # =====================================

    notes = load_notes()


    if not notes:

        return jsonify({

            "error":
            "Physics notes are not loaded yet. "
            "Please upload/build your notes first."

        }), 400


    # =====================================
    # GET QUESTION
    # =====================================

    question = request.form.get(
        "question",
        ""
    ).strip()


    # =====================================
    # GET IMAGE
    # =====================================

    image = request.files.get("image")


    if not question and not image:

        return jsonify({

            "error":
            "Please enter a question or upload an image."

        }), 400


    try:

        # =================================
        # PROMPT
        # =================================

        prompt = f"""
You are a Physics AI tutor.

The student has provided a Physics question.

Student text:

{question if question else "No text. Read the uploaded image."}


================ PHYSICS NOTES ================

{notes}

=================================================


STRICT RULES:

1. Treat these Physics notes as the PRIMARY SOURCE.

2. Find the relevant chapter, topic,
concept and formula from the notes.

3. Base the answer on these notes whenever
the required information is available.

4. Follow the terminology and method from
the notes whenever possible.

5. If an image is provided, carefully read:
- numbers
- equations
- symbols
- diagrams
- handwritten text

6. Do not invent formulas.

7. If the required information is NOT present
in the notes, clearly say:

"यह जानकारी दिए गए notes में नहीं मिली।"

8. You may perform calculations using formulas
present in the notes.

9. Explain the solution step-by-step.

10. Use proper LaTeX.

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
"""


        contents = []


        # =================================
        # IMAGE
        # =================================

        if image:

            image_bytes = image.read()


            if not image_bytes:

                return jsonify({
                    "error": "Uploaded image is empty."
                }), 400


            mime_type = (
                image.mimetype
                or "image/jpeg"
            )


            contents.append(

                types.Part.from_bytes(

                    data=image_bytes,

                    mime_type=mime_type

                )

            )


        # =================================
        # TEXT PROMPT
        # =================================

        contents.append(prompt)


        # =================================
        # GEMINI
        # =================================

        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=contents

        )


        return jsonify({

            "answer":
            response.text

        })


    except Exception as e:

        return jsonify({

            "error":
            str(e)

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
