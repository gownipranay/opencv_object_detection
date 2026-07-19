#!/usr/bin/env python3
"""Flask web UI for the AI Resume Ranker.

Upload a job description and one or more resumes; get back a ranked list
with an explainable score breakdown (text similarity + skill overlap).
"""
import tempfile
from pathlib import Path

from flask import Flask, render_template, request

from resume_ranker import extract_text, rank_resumes

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload cap

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}


def _save_and_extract(upload, tmp_dir: Path) -> str:
    suffix = Path(upload.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {upload.filename}")
    dest = tmp_dir / upload.filename
    upload.save(dest)
    return extract_text(dest)


@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None

    if request.method == "POST":
        job_file = request.files.get("job_description")
        job_text_field = request.form.get("job_description_text", "").strip()
        resume_files = [f for f in request.files.getlist("resumes") if f.filename]

        if not resume_files:
            error = "Please upload at least one resume."
        else:
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    tmp_dir = Path(tmp)

                    if job_file and job_file.filename:
                        job_text = _save_and_extract(job_file, tmp_dir)
                    elif job_text_field:
                        job_text = job_text_field
                    else:
                        raise ValueError("Please provide a job description (file or text).")

                    resumes = {}
                    for resume_file in resume_files:
                        resumes[resume_file.filename] = _save_and_extract(resume_file, tmp_dir)

                    ranked = rank_resumes(job_text, resumes)
                    results = [r.as_dict() for r in ranked]
            except ValueError as exc:
                error = str(exc)

    return render_template("index.html", results=results, error=error)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
