import requests
import docx
from flask import current_app
from openai import OpenAI

# extract text from docx URL
def extract_text_from_docx_url(file_url):
    resp = requests.get(file_url)
    with open("temp.docx", "wb") as f:
        f.write(resp.content)

    doc = docx.Document("temp.docx")
    text = "\n".join([p.text for p in doc.paragraphs])
    return text


def evaluate_assignment_from_url(file_url):
    """
    Download docx → extract text → send to OpenAI → get:
    - Score (0–100)
    - Detailed feedback
    - Strengths / weaknesses
    """

    text = extract_text_from_docx_url(file_url)

    client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"])

    prompt = f"""
    You are an expert professor. Evaluate the following student assignment.

    REQUIREMENTS:
    - Give a score from 0 to 100 (strict but fair)
    - Provide detailed feedback (3–5 paragraphs)
    - Identify strengths and weaknesses
    - Be formal and helpful

    STUDENT ASSIGNMENT:
    ---------------------
    {text}
    ---------------------

    Now respond in JSON with EXACT keys:
    {{
      "score": number,
      "feedback": "string"
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are an expert evaluator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    import json
    result = json.loads(response.choices[0].message.content)

    score = result.get("score", 75)
    feedback = result.get("feedback", "No feedback generated.")

    return score, feedback
