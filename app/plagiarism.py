from difflib import SequenceMatcher
from .evaluation import extract_text_from_docx_url
from .supabase_service import get_submissions_for_assignment

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def calculate_plagiarism_for_assignment(assignment_id: str, new_file_url: str) -> float:
    """
    Compare new submission with previous ones for the same assignment (Supabase).
    """
    previous_submissions = get_submissions_for_assignment(assignment_id)
    if not previous_submissions:
        return 0.0

    new_text = extract_text_from_docx_url(new_file_url)
    max_sim = 0.0

    for _, sub in previous_submissions.items():
        url = sub.get("file_url")
        if not url:
            continue
        try:
            existing_text = extract_text_from_docx_url(url)
            sim = similarity(new_text, existing_text)
            if sim > max_sim:
                max_sim = sim
        except Exception:
            continue

    return round(max_sim * 100, 2)
