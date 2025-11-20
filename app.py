from flask import Flask, render_template, request, jsonify
from scout_client import ask_scout

app = Flask(__name__)

app = Flask(__name__)
app.secret_key = 'secret_-DrRVr2LhcZjgjflld_UeGe5Xc4hnma-XEyWbBYYavI'  # ⚠️ Change this

# ==== Scout Configuration ====
SCOUT_API_KEY = "secret_-DrRVr2LhcZjgjflld_UeGe5Xc4hnma-XEyWbBYYavI"  # ⚠️ Use env var in production
SCOUT_COLLECTION_ID = "col_cme35qd2600j10gs6nacyppzf"
SCOUT_TABLE_ID = "tbl_cme35qdbq00or0gs6nz4vgad3"
SCOUT_API_BASE_URL = "https://api-prod.scoutos.com/v2"


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
