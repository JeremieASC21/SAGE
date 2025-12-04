from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI
from sage_prompt import SAGE_SYSTEM_PROMPT
from advisor import search_programs  # use your PDF search logic

app = Flask(__name__)

# OpenAI client will read OPENAI_API_KEY from the environment
client = OpenAI()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about-us")
def about_us():
    return render_template("about-us.html")


@app.route("/sage")
def sage():
    return render_template("sage.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a question so I can help."})

    # 1️⃣ Search your UW program database using the PDF code
    try:
        matches = search_programs(user_message)
    except Exception as e:
        print("Error in search_programs:", e)
        matches = []

    # 2️⃣ Build a concise context string from the top matches
    top_matches = matches[:5]

    if top_matches:
        context_lines = []
        for prog in top_matches:
            name = prog.get("name", "Unknown program")
            location = prog.get("location", "Unknown location")
            url = prog.get("program_url", "No URL available")
            themes = ", ".join(prog.get("tags", {}).get("themes", []))
            academics = ", ".join(prog.get("tags", {}).get("academics", []))

            context_lines.append(
                f"- {name} ({location})\n"
                f"  URL: {url}\n"
                f"  Academics: {academics or 'n/a'}\n"
                f"  Themes: {themes or 'n/a'}"
            )

        context_text = "\n".join(context_lines)
    else:
        context_text = (
            "No matching programs were found in the database for this query. "
            "You may still suggest high-level advising next steps, but do not invent program names."
        )

    # 3️⃣ Build the messages for the model
    messages = [
        {
            "role": "system",
            "content": SAGE_SYSTEM_PROMPT,
        },
        {
            "role": "system",
            "content": (
                "You are SAGE, a UW–Madison study abroad and internship assistant. "
                "Use ONLY the following program list when recommending specific opportunities. "
                "Whenever you mention a program, include its exact name and URL. "
                "If the student asks about internships, prioritize programs whose themes include "
                "internship, career, or professional development."
            ),
        },
        {
            "role": "system",
            "content": "Here are the database matches for this student's question:\n\n"
                       f"{context_text}",
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]

    # 4️⃣ Call OpenAI
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # chat-capable model
            messages=messages,
            temperature=0.4,
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        print("Error calling OpenAI:", e)
        reply = "[Error contacting SAGE backend. Please try again later.]"

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
