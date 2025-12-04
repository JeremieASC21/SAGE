from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta
from openai import OpenAI

from sage_prompt import SAGE_SYSTEM_PROMPT
from advisor import search_programs
from internship_tips import INTERNSHIP_TIPS
from companies import get_companies_for_query

app = Flask(__name__)

# Needed for session-based chat history
app.secret_key = "CHANGE_ME_TO_SOMETHING_RANDOM_AND_SECRET"
app.permanent_session_lifetime = timedelta(minutes=30)

# OpenAI client will read OPENAI_API_KEY from the environment
client = OpenAI()

INTERNSHIP_KEYWORDS = [
    "internship",
    "internships",
    "interning",
    "co-op",
    "co op",
    "coop",
    "summer internship",
    "global internship",
]

COMPANY_KEYWORDS = [
    "company",
    "companies",
    "employer",
    "employers",
    "work for",
    "apply to",
    "where should i apply",
]


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

    # --- Session-based conversation history ---
    session.permanent = True
    if "history" not in session:
        session["history"] = []

    history = session["history"]
    # Add the current user message to the history
    history.append({"role": "user", "content": user_message})

    # Detect intents from this message
    q_lower = user_message.lower()
    internship_interest = any(kw in q_lower for kw in INTERNSHIP_KEYWORDS)
    company_interest = any(kw in q_lower for kw in COMPANY_KEYWORDS)

    # 1️⃣ Search programs in your UW database based on THIS question
    try:
        matches = search_programs(user_message)
    except Exception as e:
        print("Error in search_programs:", e)
        matches = []

    # 2️⃣ Build concise context from matches
    top_matches = matches[:5]

    if top_matches:
        context_lines = []
        for prog in top_matches:
            name = prog.get("name", "Unknown program")
            location = prog.get("location", "Unknown location")
            url = prog.get("program_url", "No URL available")
            prog_type = prog.get("type", "study_abroad")
            themes = ", ".join(prog.get("tags", {}).get("themes", []))
            academics = ", ".join(prog.get("tags", {}).get("academics", []))

            context_lines.append(
                f"- {name} ({location})\n"
                f"  Type: {prog_type}\n"
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

    # 2.5️⃣ Build company context if needed (for this question)
    company_context_text = ""
    if company_interest:
        major_label, companies = get_companies_for_query(user_message)
        if companies:
            lines = [f"Suggested employers for major or interest: {major_label}"]
            for c in companies:
                lines.append(f"- {c['name']} ({c['industry']}): {c['notes']}")
            company_context_text = "\n".join(lines)

    # 3️⃣ Build messages for the model
    messages = [
        {"role": "system", "content": SAGE_SYSTEM_PROMPT},
        {
            "role": "system",
            "content": (
                "You are SAGE, a UW–Madison study abroad and internship assistant. "
                "Use ONLY the following program list when recommending specific opportunities, "
                "and whenever you mention a program, include its exact name and URL. "
                "If the student asks about internships, prioritize programs whose themes include "
                "internship, career, or professional development. "
                "If there are no matching programs for the student’s requested location or criteria, "
                "do NOT recommend different study abroad locations from the list; instead, provide general "
                "study abroad and travel tips for the location they asked about, plus high-level UW–Madison "
                "advising guidance. Only suggest alternative locations if the student explicitly says they "
                "are open to other places."
            ),
        },
        {
            "role": "system",
            "content": (
                "Here are the database matches for this student's current question:\n\n"
                f"{context_text}"
            ),
        },
    ]

    # Internship search advice
    if internship_interest:
        messages.append(
            {
                "role": "system",
                "content": (
                    "The student is asking about internships. Use the following UW–Madison-aligned internship "
                    "search advice to guide your response. Paraphrase it naturally; do not just dump bullets:\n\n"
                    f"{INTERNSHIP_TIPS}"
                ),
            }
        )

    # Company/employer suggestions or general employer advice
    if company_interest and company_context_text:
        messages.append(
            {
                "role": "system",
                "content": (
                    "The student is asking which companies or employers they should apply to. "
                    "Use the following employer suggestion list as examples. "
                    "You may group them by type (big tech, local, startup, etc.) and explain why they "
                    "are relevant for the student's major, but do not claim this is a complete list:\n\n"
                    f"{company_context_text}"
                ),
            }
        )
    elif company_interest and not company_context_text:
        messages.append(
            {
                "role": "system",
                "content": (
                    "The student is asking which companies or employers they should apply to, "
                    "but there is no curated company list available for their major or query. "
                    "Do NOT invent specific companies. Instead, give general advice on:\n"
                    "- How to use Handshake and LinkedIn to discover relevant employers\n"
                    "- How to search by industry/role instead of specific company names\n"
                    "- How to research whether a company is a good fit (culture, values, roles)\n"
                    "- How to talk with advisors, alumni, and peers to generate a personalized employer list.\n"
                    "If helpful, you may ask the student for their major or field of interest so you can be more specific."
                ),
            }
        )

    # 3.5️⃣ Attach the entire conversation history (user + assistant messages)
    # This lets SAGE remember earlier majors, locations, etc.
    messages.extend(history)

    # 4️⃣ Call OpenAI
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        print("Error calling OpenAI:", e)
        reply = "[Error contacting SAGE backend. Please try again later.]"

    # Save assistant reply to history
    history.append({"role": "assistant", "content": reply})
    session["history"] = history

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
