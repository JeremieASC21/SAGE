import requests

app = Flask(__name__)
app.secret_key = 'secret_RknMrEzuRZlSNnelIZfZz81f47yBxpfAft29fbEgZBk'  # ⚠️ Change this

# ==== Scout Configuration ====
SCOUT_API_KEY = "secret_RknMrEzuRZlSNnelIZfZz81f47yBxpfAft29fbEgZBk"  # ⚠️ Use env var in production
SCOUT_COLLECTION_ID = "col_cme35qd2600j10gs6nacyppzf"
SCOUT_TABLE_ID = "tbl_cme35qdbq00or0gs6nz4vgad3"
SCOUT_API_BASE_URL = "https://api-prod.scoutos.com/v2"


# Example: multiple relevant collections in Scout
COLLECTIONS = [
    "study_abroad_opportunities",
    "international_internships",
    "domestic_internships",
    "funding_and_scholarships"
]

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SCOUT_API_KEY}"
}

def ask_scout(question):
    payload = {
        "question": question,
        "collections": COLLECTIONS,
        "top_k": 5
    }

    response = requests.post(SCOUT_ENDPOINT, json=payload, headers=headers)

    if response.status_code != 200:
        return f"[Error contacting ScoutOS: {response.text}]"

    data = response.json()
    return data.get("answer", "Sorry, I couldn’t find anything related to that.")
