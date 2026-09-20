from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Physics AI Solver Backend is Working!"

@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Question is required"
        }), 400

    return jsonify({
        "answer": "Question received successfully.",
        "question": question
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
