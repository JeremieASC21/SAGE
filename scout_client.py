import requests

SCOUT_API_KEY = "secret_-DrRVr2LhcZjgjflld_UeGe5Xc4hnma-XEyWbBYYavI"
SCOUT_ENDPOINT = "https://api.scoutos.ai/v1/query"

# Use the actual names from your Scout dashboard
COLLECTIONS = [
    "Study Abroad",
    "Internship",
    "Usage"
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
