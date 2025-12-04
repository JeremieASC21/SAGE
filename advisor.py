# advisor.py
from typing import List, Dict
from programs import PROGRAMS

def normalize(text: str) -> str:
    return text.lower().strip()

ACADEMIC_SYNONYMS = {
    "biology": ["biology", "bio", "zoology", "life science", "life sciences"],
    "computer science": ["computer science", "cs", "comp sci", "software"],
    "public health": ["public health", "global health", "health"],
    "environmental studies": ["environmental studies", "environment science", "ecology"],
    "spanish": ["spanish", "español", "spanish language"],
}

REGION_SYNONYMS = {
    "europe": ["europe", "european"],
    "latin america": ["latin america", "latam", "south america"],
    "scandinavia": ["scandinavia", "nordic", "denmark", "copenhagen"],
    "australia": ["australia", "aussie"],
    "italy": ["italy", "italian", "rome"],
    "prague": ["prague", "czech republic"],
    "costa rica": ["costa rica", "san jose", "monteverde"],
    "panama": ["panama", "bocas del toro"],
}

INTERNSHIP_KEYWORDS = [
    "internship",
    "internships",
    "interning",
    "co-op",
    "co op",
    "coop",
    "placement",
    "work experience",
    "professional experience",
]


def search_programs(query: str) -> List[Dict]:
    """
    Hybrid search over the PROGRAMS dictionary based on keywords, synonyms, and
    optionally internship interest.
    """
    q = normalize(query)
    results = []

    # Detect if the user is clearly asking about internships
    internship_interest = any(word in q for word in INTERNSHIP_KEYWORDS)

    for prog in PROGRAMS.values():
        base_score = 0
        name_text = normalize(prog["name"])
        loc_text = normalize(prog["location"])
        tags = prog.get("tags", {})
        academics_tags = " ".join(tags.get("academics", [])).lower()
        themes_tags = " ".join(tags.get("themes", [])).lower()
        prog_type = prog.get("type", "study_abroad")

        # Direct name/location match
        if q and name_text.find(q) != -1:
            base_score += 3
        if q and loc_text.find(q) != -1:
            base_score += 2

        # Token-based partial match
        for token in q.split():
            if token and token in name_text:
                base_score += 1
            if token and token in loc_text:
                base_score += 1

        # Tag-based scoring
        for group, tag_list in tags.items():
            for tag in tag_list:
                if normalize(tag) in q:
                    base_score += 2

        # Academic synonyms
        for key, syns in ACADEMIC_SYNONYMS.items():
            if any(s in q for s in syns) and key in academics_tags:
                base_score += 2

        # Region synonyms
        for key, syns in REGION_SYNONYMS.items():
            if any(s in q for s in syns) and any(k in loc_text for k in syns):
                base_score += 1

        # Internship boost
        if internship_interest:
            if prog_type in ("internship", "study_abroad+internship"):
                base_score += 3
            if any(word in themes_tags for word in ["internship", "internship-style", "career", "professional"]):
                base_score += 2

        if base_score > 0:
            results.append((base_score, prog))

    results.sort(key=lambda x: x[0], reverse=True)
    return [p for score, p in results]
