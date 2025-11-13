from flask import Flask, render_template, request, jsonify
from scout_client import ask_scout

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("templates/index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    # Query ScoutOS
    bot_reply = ask_scout(user_message)

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
