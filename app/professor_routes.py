from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import textwrap
import traceback


# Blueprint (must be first)

professor_bp = Blueprint("professor", __name__, url_prefix="/professor")



# Dashboard

@professor_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "professor":
        return redirect(url_for("student.dashboard"))

    try:
        from .supabase_service import get_all_assignments
        assignments = get_all_assignments() or {}
    except Exception as e:
        current_app.logger.exception("Failed to load assignments")
        assignments = {}

    return render_template("professor_dashboard.html", assignments=assignments)



# Create Assignment

@professor_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_assignment_route():
    if current_user.role != "professor":
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        due_date = request.form.get("due_date")

        if not title:
            flash("Title is required", "warning")
            return redirect(request.url)

        try:
            from .supabase_service import create_assignment
            data = {
                "title": title,
                "description": description,
                "due_date": due_date,
                "created_by": current_user.email,
            }
            res = create_assignment(data)
            flash("Assignment created.", "success")
            return redirect(url_for("professor.dashboard"))
        except Exception as e:
            current_app.logger.exception("Could not create assignment")
            flash("Failed to create assignment.", "danger")

    return render_template("create_assignment.html")



# View Submissions

@professor_bp.route("/submissions/<assignment_id>")
@login_required
def view_submissions(assignment_id):
    if current_user.role != "professor":
        return redirect(url_for("student.dashboard"))

    try:
        from .supabase_service import get_submissions_for_assignment, get_assignment
        submissions = get_submissions_for_assignment(assignment_id) or {}
        assignment = get_assignment(assignment_id) or {}
    except Exception as e:
        current_app.logger.exception("Could not load submissions")
        submissions = {}
        assignment = {}

    return render_template("view_submissions.html", submissions=submissions, assignment=assignment)



# Download PDF Report

@professor_bp.route("/report/<assignment_id>/<submission_id>/pdf")
@login_required
def download_pdf_report(assignment_id, submission_id):
    # Only professors allowed here
    if current_user.role != "professor":
        return "Forbidden", 403

    try:
        from .supabase_service import get_submissions_for_assignment, get_assignment

        subs = get_submissions_for_assignment(assignment_id) or {}

        # Support dict or list structures
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
            return redirect(url_for("professor.view_submissions", assignment_id=assignment_id))

        assignment = get_assignment(assignment_id) or {}

        # Build PDF
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        left = 50
        top = height - 50

        # Header
        c.setFont("Helvetica-Bold", 18)
        c.drawString(left, top, f"Report — {assignment.get('title', 'Assignment')}")
        c.setFont("Helvetica", 10)
        c.drawString(width - 220, top, f"Assignment ID: {assignment_id}")

        # Metadata
        y = top - 36
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left, y, "Submission Details:")
        y -= 18
        c.setFont("Helvetica", 11)
        c.drawString(left, y, f"Student: {submission.get('student_email', '—')}")
        y -= 16
        c.drawString(left, y, f"Submission ID: {submission.get('id', submission_id)}")
        y -= 16
        c.drawString(left, y, f"Score: {submission.get('score', '—')}")
        y -= 16
        c.drawString(left, y, f"Plagiarism: {submission.get('plagiarism_percent', 0)}%")
        y -= 22

        # Feedback
        c.setFont("Helvetica-Bold", 13)
        c.drawString(left, y, "Feedback:")
        y -= 18
        c.setFont("Helvetica", 11)
        feedback = submission.get("feedback", "") or ""
        for paragraph in feedback.splitlines() or [""]:
            for line in textwrap.wrap(paragraph, width=90) or [""]:
                if y < 60:
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 11)
                c.drawString(left, y, line)
                y -= 14

        # AI summary if exists
        if submission.get("ai_summary"):
            if y < 120:
                c.showPage()
                y = height - 50
            y -= 8
            c.setFont("Helvetica-Bold", 13)
            c.drawString(left, y, "AI Summary:")
            y -= 18
            c.setFont("Helvetica", 11)
            for paragraph in str(submission.get("ai_summary")).splitlines():
                for line in textwrap.wrap(paragraph, width=90):
                    if y < 60:
                        c.showPage()
                        y = height - 50
                        c.setFont("Helvetica", 11)
                    c.drawString(left, y, line)
                    y -= 14

        c.showPage()
        c.save()
        buffer.seek(0)

        filename = f"prof_report_{submission_id}.pdf"
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

    except Exception as exc:
        current_app.logger.exception("Error generating professor PDF report")
        traceback.print_exc()
        flash("Could not generate PDF report. Check server logs.", "danger")
        return redirect(url_for("professor.view_submissions", assignment_id=assignment_id))
