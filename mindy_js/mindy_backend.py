from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory mock data for simplicity
data = {
    "summary": {
        "headline": "AI is transforming education rapidly.",
        "summary": "AI tools like Mindy are helping learners personalize study plans and stay on track.",
        "suggestion": "Explore AI courses this weekend to gain an edge."
    },
    "reminders": [
        {"task": "Read 10 pages of a book", "done": True},
        {"task": "Meditate for 10 minutes", "done": False},
        {"task": "Practice one coding problem", "done": False}
    ],
    "interview_questions": [
        "Tell me about yourself",
        "What are your strengths and weaknesses?",
        "Why do you want this job?"
    ],
    "study_progress": [
        {"name": "Week 1", "Progress": 20},
        {"name": "Week 2", "Progress": 40},
        {"name": "Week 3", "Progress": 65},
        {"name": "Week 4", "Progress": 80}
    ],
    "savings": {
        "goal": 5000,
        "saved": 2500
    }
}

@app.route("/api/summary")
def get_summary():
    return jsonify(data["summary"])

@app.route("/api/reminders")
def get_reminders():
    return jsonify(data["reminders"])

@app.route("/api/interview")
def get_interview_questions():
    return jsonify(data["interview_questions"])

@app.route("/api/study")
def get_study_data():
    return jsonify(data["study_progress"])

@app.route("/api/savings")
def get_savings():
    return jsonify(data["savings"])

@app.route("/api/savings/add", methods=["POST"])
def add_savings():
    amount = request.json.get("amount", 0)
    data["savings"]["saved"] += amount
    return jsonify(data["savings"])

if __name__ == "__main__":
    app.run(debug=True)
