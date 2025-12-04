from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI
from sage_prompt import SAGE_SYSTEM_PROMPT

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/about-us')
def about_us():
    return render_template('about-us.html')

@app.route('/sage')
def sage():
    return render_template('sage.html')


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a question so I can help."})

    # If you have custom UW content, you can load it here and pass as context
    # For now, we'll use an empty context string.
    context = ""

    messages = [
        {"role": "system", "content": SAGE_SYSTEM_PROMPT},
        {
            "role": "system",
            "content": f"Context:\n{context}\n\nAnswer the student using only this context plus general advising best practices."
        },
        {"role": "user", "content": user_message},
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",  # or any other chat-capable model you like
            messages=messages,
            temperature=0.4,
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        print("Error calling OpenAI:", e)
        reply = "[Error contacting SAGE AI backend. Please try again later.]"

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
