from flask import Flask, render_template, redirect, url_for, session, request
from modules.news_digest import fetch_news_by_topic, TOPIC_LABELS

app = Flask(__name__)
app.secret_key = "your_secret"

@app.route("/")
def dashboard():
    headlines = session.get("headlines", [])
    selected_topic = session.get("topic", "tech")
    return render_template("dashboard.html", headlines=headlines, selected_topic=selected_topic, topics=TOPIC_LABELS)

@app.route("/digest/refresh", methods=["POST"])
def refresh_digest():
    topic = request.form.get("topic", "tech")
    headlines = fetch_news_by_topic(topic)
    session["headlines"] = headlines
    session["topic"] = topic
    return redirect(url_for("dashboard"))

if __name__ == '__main__':
    app.run(debug=True)