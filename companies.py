# companies.py

COMPANIES_BY_MAJOR = {
    "computer science": [
        {
            "name": "Google",
            "industry": "Big tech / software",
            "notes": "Large-scale software engineering, infrastructure, ML, and product roles.",
        },
        {
            "name": "Microsoft",
            "industry": "Big tech / software",
            "notes": "Cloud (Azure), productivity tools, operating systems, and developer tools.",
        },
        {
            "name": "Amazon",
            "industry": "Big tech / e-commerce / cloud",
            "notes": "Software roles in AWS, logistics, retail tech, and machine learning.",
        },
        {
            "name": "Meta",
            "industry": "Social / AR/VR / ads",
            "notes": "Front-end, back-end, infrastructure, and research roles on large user-facing products.",
        },
        {
            "name": "Apple",
            "industry": "Consumer hardware / software",
            "notes": "Systems, mobile, hardware-software integration, and UX-heavy roles.",
        },
        {
            "name": "NVIDIA",
            "industry": "Semiconductors / AI / graphics",
            "notes": "GPU programming, AI infrastructure, and high-performance computing.",
        },
        {
            "name": "Epic Systems",
            "industry": "Healthcare software",
            "notes": "Madison-area employer; builds large healthcare information systems.",
        },
        {
            "name": "FIS Global and other FinTech firms",
            "industry": "Financial technology",
            "notes": "Payment processing, financial infrastructure, and enterprise software.",
        },
        {
            "name": "Smaller startups & local firms",
            "industry": "Varies",
            "notes": "Early-stage or local companies where you may get broad responsibilities quickly.",
        },
    ],

    "data science": [
        {
            "name": "Spotify",
            "industry": "Consumer tech / data",
            "notes": "Recommender systems and analytics.",
        },
        {
            "name": "Capital One",
            "industry": "FinTech / banking",
            "notes": "Data science roles in risk, credit, and customer analytics.",
        },
    ],
}


def guess_major_from_query(query: str):
    q = query.lower()
    if "computer science" in q or "cs major" in q or " cs " in q or q.startswith("cs "):
        return "computer science"
    if "data science" in q:
        return "data science"
    return None


def get_companies_for_query(query: str):
    """
    Return (major_label, list_of_company_dicts).

    If we cannot map the query to a known major, we return (None, []) so that
    the chatbot will give only general advice and will NOT list specific companies.
    """
    major_key = guess_major_from_query(query)
    if major_key is None:
        return None, []

    companies = COMPANIES_BY_MAJOR.get(major_key, [])
    return major_key, companies
