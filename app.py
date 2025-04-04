import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import google.generativeai as genai
from docx import Document

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Ensure UPLOAD_FOLDER exists
UPLOAD_FOLDER = "generated_papers"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Google Gemini AI API Key (Use your own valid API key)
genai.configure(api_key="AIzaSyB5RRdbSHe9K2FYRTrcGpiIhEjw-myna1Q")

# Dummy users for authentication
users = {"admin": "password123"}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["username"] = username
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

def generate_questions(syllabus_text):
    """Generate a structured question paper following the required format."""
    prompt = f"""
    Generate a **B.Tech VI Semester (R20) Computer Networks Exam** based on the given syllabus:

    **PART A (10 questions, 2 marks each)**
    - Short-answer questions covering different syllabus topics.
    - Each question should have a **CO (Course Outcome) Number** and a **BT (Bloom’s Taxonomy) Level**.

    **PART B (5 units, 10 marks each)**
    - Each unit should have **one long-form question** with an **alternative OR question**.
    - Ensure each question is properly numbered and formatted.

    Syllabus Topics: {syllabus_text}
    """

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return response.text  # Returns formatted AI-generated questions

@app.route("/generate", methods=["GET", "POST"])
def generate():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        exam_title = request.form.get("exam_title", "B.TECH VI SEMESTER (R20)")
        subject = request.form.get("subject", "COMPUTER NETWORKS")
        syllabus_text = request.form["syllabus_text"]

        # Generate AI-based questions
        question_paper_text = generate_questions(syllabus_text)

        # Create Word Document
        doc = Document()
        doc.add_paragraph(f"{exam_title}\n(AUTONOMOUS)\n"
                          f"REGULAR / SUPPLEMENTARY EXAMINATIONS - JUN 2024\n"
                          f"{subject}\n"
                          "Time: 3 Hours                        Max. Marks: 70\n"
                          "---------------------------------------------------------------\n",
                          style="Title")

        doc.add_paragraph(question_paper_text, style="Normal")

        # Save Document
        doc_filename = os.path.join(app.config["UPLOAD_FOLDER"], "Generated_Question_Paper.docx")
        doc.save(doc_filename)

        return send_file(doc_filename, as_attachment=True)

    return render_template("generate.html")

if __name__ == "__main__":
    app.run(debug=True)
