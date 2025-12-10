from supabase import create_client
from flask import current_app


def get_supabase():
    url = current_app.config["SUPABASE_URL"]
    key = current_app.config["SUPABASE_KEY"]
    return create_client(url, key)


# ---------------- ASSIGNMENTS ---------------- #

def create_assignment(title, description, due_date):
    supabase = get_supabase()
    data = {"title": title, "description": description, "due_date": due_date}
    supabase.table("assignments").insert(data).execute()


def get_all_assignments():
    supabase = get_supabase()
    res = supabase.table("assignments").select("*").order("created_at").execute()
    rows = res.data or []
    assignments = {row["id"]: row for row in rows}
    return assignments


def get_assignment(assignment_id):
    supabase = get_supabase()
    res = supabase.table("assignments").select("*").eq("id", assignment_id).execute()
    rows = res.data or []
    return rows[0] if rows else None


# ---------------- SUBMISSIONS ---------------- #

def add_submission(assignment_id, student_email, file_url, score, plagiarism, feedback):
    supabase = get_supabase()

    data = {
        "assignment_id": assignment_id,
        "student_email": student_email,
        "file_url": file_url,
        "score": score,
        "plagiarism_percent": plagiarism,
        "feedback": feedback,
    }

    res = supabase.table("submissions").insert(data).execute()

    rows = res.data or []
    return rows[0]["id"]


def get_submissions_for_assignment(assignment_id):
    supabase = get_supabase()

    res = (
        supabase.table("submissions")
        .select("*")
        .eq("assignment_id", assignment_id)
        .order("created_at")
        .execute()
    )

    rows = res.data or []
    submissions = {row["id"]: row for row in rows}
    return submissions
