# advisor.py
from typing import List, Dict
from programs import PROGRAMS


ACADEMIC_SYNONYMS = {
    "biology": ["bio", "life science", "wildlife", "ecology", "biodiversity", "zoology"],
    "engineering": ["engineer", "stem", "tech", "technology"],
    "business": ["marketing", "management", "finance"],
    "public health": ["global health", "health", "community health"],
}
REGION_SYNONYMS = {
    "europe": ["europe", "european", "italy", "denmark", "copenhagen", "prague"],
    "latin america": ["latin america", "south america", "argentina", "buenos aires"],
    "tropical": ["tropical", "panama", "costa rica", "bocas del toro"],
    "scandinavia": ["scandinavia", "denmark", "copenhagen"],
}


def normalize(text: str) -> str:
    return text.lower()


def search_programs(query: str) -> List[Dict]:
    """
    Hybrid search over the PROGRAMS dictionary based on keywords + synonyms.
    """
    q = normalize(query)
    results = []
    for prog in PROGRAMS.values():
        base_score = 0
        # Direct name/location match
        if normalize(prog["name"]).find(q) != -1:
            base_score += 3
        if normalize(prog["location"]).find(q) != -1:
            base_score += 2
        # Tag-based scoring
        for group, tag_list in prog["tags"].items():
            for tag in tag_list:
                if normalize(tag) in q:
                    base_score += 2
        # Academic synonyms
        for key, syns in ACADEMIC_SYNONYMS.items():
            if any(s in q for s in syns):
                if key in " ".join(prog["tags"].get("academics", [])).lower():
                    base_score += 2
        # Region synonyms
        for key, syns in REGION_SYNONYMS.items():
            if any(s in q for s in syns):
                if any(k in prog["location"].lower() for k in syns):
                    base_score += 1
        if base_score > 0:
            results.append((base_score, prog))
    results.sort(key=lambda x: x[0], reverse=True)
    return [p for score, p in results]


def format_program_sheet(prog: Dict) -> str:
    """Return the advising-sheet style text for a single program."""
    summary = prog.get("summary") or "Program summary to be added."
    learning_outcomes = prog.get("learning_outcomes") or []
    recommended_majors = prog.get("recommended_majors") or []
    difficulty = prog.get("difficulty") or "To be determined"
    living_env = prog.get("living_environment") or "To be added"
    cost_notes = prog.get("cost_accessibility") or "To be added"
    lines = []

    lines.append("====================================================")
    lines.append(f"PROGRAM: {prog['name']}")
    lines.append(f"LOCATION: {prog['location']}")
    lines.append("====================================================\n")
    lines.append("■ Program Overview")
    lines.append(summary.strip() + "\n")
    lines.append("----------------------------------------------------\n")
    lines.append("■ Learning Outcomes")
    if learning_outcomes:
        for lo in learning_outcomes:
            lines.append(f" {lo}")
    # Blank bullets for manual editing
    lines.append(" ")
    lines.append(" ")
    lines.append("\n")
    lines.append("■ Recommended Majors / Academic Fit")
    if recommended_majors:
        for m in recommended_majors:
            lines.append(f" {m}")
    lines.append(" ")
    lines.append("\n")
    lines.append("■ Difficulty / Rigor Level")
    lines.append(difficulty + "\n")
    lines.append("■ Living Environment")
    lines.append(living_env + "\n")
    lines.append("■ Cost & Accessibility Notes")
    lines.append(cost_notes + "\n")
    lines.append("====================================================")
    return "\n".join(lines)


def get_program_by_id(program_id: str) -> Dict:
    """Helper to look up a program by its id string."""
    return PROGRAMS.get(program_id)
