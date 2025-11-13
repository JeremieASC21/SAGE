import requests

#change API key

SCOUT_API_KEY = "YOUR_SCOUT_API_KEY"
SCOUT_ENDPOINT = "https://api.scoutos.ai/v1/query"

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
