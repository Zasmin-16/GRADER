# app/student_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import textwrap


# MUST BE DEFINED FIRST!!!

student_bp = Blueprint("student", __name__, url_prefix="/student")



# Helpers

ALLOWED_EXTENSIONS = {".docx"}

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS



# Student Dashboard

@student_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "student":
        return redirect(url_for("professor.dashboard"))

    from .supabase_service import get_all_assignments, get_submissions_for_assignment

    assignments = get_all_assignments()
    my_submissions = []

    for aid, a in assignments.items():
        subs = get_submissions_for_assignment(aid)

        for sid, s in subs.items():
            if s.get("student_email") == current_user.email:
                s["submission_id"] = sid
                s["assignment"] = {"id": aid, "title": a["title"]}
                my_submissions.append(s)

    return render_template("student_dashboard.html", assignments=assignments, my_submissions=my_submissions)



# Submit Assignment

@student_bp.route("/submit/<assignment_id>", methods=["GET", "POST"])
@login_required
def submit_assignment(assignment_id):
    if current_user.role != "student":
        return redirect(url_for("professor.dashboard"))

    if request.method == "POST":
        file = request.files.get("file")

        if not file or not file.filename:
            flash("Upload a .docx file", "warning")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Only .docx files allowed", "danger")
            return redirect(request.url)

        try:
            from .cloudinary_service import upload_docx_to_cloudinary
            from .evaluation import evaluate_assignment_from_url
            from .plagiarism import calculate_plagiarism_for_assignment
            from .supabase_service import add_submission

            file_url = upload_docx_to_cloudinary(file)

            score, feedback = evaluate_assignment_from_url(file_url)
            plagiarism = calculate_plagiarism_for_assignment(assignment_id, file_url)

            submission_id = add_submission(
                assignment_id,
                current_user.email,
                file_url,
                score,
                plagiarism,
                feedback,
            )

            flash("Submitted successfully!", "success")
            return redirect(
                url_for("student.view_result", assignment_id=assignment_id, submission_id=submission_id)
            )

        except Exception as e:
            print("Submit error:", e)
            flash("Submission failed!", "danger")

    return render_template("submit_assignment.html")



# View Result

@student_bp.route("/result/<assignment_id>/<submission_id>")
@login_required
def view_result(assignment_id, submission_id):
    from .supabase_service import get_submissions_for_assignment, get_assignment

    subs = get_submissions_for_assignment(assignment_id)
    submission = subs.get(submission_id)
    assignment = get_assignment(assignment_id)

    if not submission:
        flash("Result not found", "warning")
        return redirect(url_for("student.dashboard"))

    return render_template(
        "student_result.html",
        submission=submission,
        assignment=assignment,
        submission_id=submission_id,
    )



# Download Report (PDF)

@student_bp.route("/download-report/<assignment_id>/<submission_id>")
@login_required
def download_my_report(assignment_id, submission_id):

    if current_user.role != "student":
        return "Forbidden", 403

    try:
        from .supabase_service import get_submissions_for_assignment, get_assignment

        subs = get_submissions_for_assignment(assignment_id) or {}

        # Find submission
        submission = None
        if isinstance(subs, dict):
            submission = subs.get(submission_id)
        elif isinstance(subs, list):
            for row in subs:
                if str(row.get("id")) == str(submission_id):
                    submission = row
                    break

        if not submission:
            flash("Submission not found.", "warning")
            return redirect(url_for("student.dashboard"))

        # Ownership check
        if submission.get("student_email") != current_user.email:
            return "Forbidden", 403

        assignment = get_assignment(assignment_id) or {}

        # Build PDF
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        width, height = A4
        left = 50
        top = height - 50

        c.setFont("Helvetica-Bold", 18)
        c.drawString(left, top, f"Report — {assignment.get('title','Assignment')}")

        c.setFont("Helvetica", 12)
        y = top - 30
        c.drawString(left, y, f"Student: {submission.get('student_email')}")
        y -= 18
        c.drawString(left, y, f"Score: {submission.get('score','—')}")
        y -= 18
        c.drawString(left, y, f"Plagiarism: {submission.get('plagiarism_percent',0)}%")
        y -= 24

        c.setFont("Helvetica-Bold", 13)
        c.drawString(left, y, "Feedback:")
        y -= 18
        c.setFont("Helvetica", 11)

        feedback = submission.get("feedback", "") or ""
        for paragraph in feedback.splitlines():
            for line in textwrap.wrap(paragraph, 90):
                if y < 60:
                    c.showPage()
                    y = height - 50
                c.drawString(left, y, line)
                y -= 14

        c.showPage()
        c.save()
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"report_{submission_id}.pdf",
            mimetype="application/pdf",
        )

    except Exception as e:
        print("PDF error:", e)
        flash("Could not generate report.", "danger")
        return redirect(
            url_for("student.view_result", assignment_id=assignment_id, submission_id=submission_id)
        )
