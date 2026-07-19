# AI Resume Ranker

An explainable, NLP-powered tool that ranks candidate resumes against a job
description. Instead of a black-box score, it tells you *why* a resume
ranked where it did: overall text similarity plus exactly which required
skills matched and which are missing.

## How it works

1. **Text extraction** — pulls raw text out of `.txt`, `.pdf`, or `.docx`
   resumes and job descriptions.
2. **TF-IDF + cosine similarity** — a dependency-free TF-IDF vectorizer
   (`resume_ranker/tfidf.py`) measures overall topical similarity between
   a resume and the job description.
3. **Skill extraction** — a curated skill taxonomy
   (`resume_ranker/skills.py`) pulls out known technical/soft skills from
   both documents and reports the exact overlap and gaps.
4. **Combined score** — the final match score blends text similarity (40%)
   and skill coverage (60%), since recruiters generally care more about
   concrete skill matches than prose similarity.

No heavyweight ML dependencies (no scikit-learn/numpy/spaCy) are required
for the core ranking logic — it's implemented in plain Python so it runs
anywhere. PDF/DOCX parsing uses lightweight optional libraries.

## Project structure

```
ai-resume-ranker/
├── app.py                    # Flask web UI
├── cli.py                    # Command-line interface
├── resume_ranker/
│   ├── tfidf.py               # Pure-Python TF-IDF + cosine similarity
│   ├── skills.py               # Skill taxonomy + extraction
│   ├── text_extract.py         # .txt / .pdf / .docx text extraction
│   └── ranker.py                # Orchestrates scoring + ranking
├── templates/index.html       # Web UI page
├── static/style.css           # Web UI styling
├── sample_data/               # Example job description + resumes
└── tests/                     # Unit tests
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Command line

```bash
python cli.py --job sample_data/job_description.txt --resumes sample_data/resumes
```

Example output:

```
1. alice_johnson.txt  —  match score: 62.0%
   text similarity: 44.9%   skill coverage: 73.3%
   matched skills: agile, aws, ci/cd, docker, flask, git, machine learning, ...
   missing skills: airflow, computer vision, data engineering, kubernetes, ...
```

### Web UI

```bash
python app.py
```

Then open http://localhost:5000, upload a job description (file or pasted
text) and one or more resumes, and view the ranked results in your browser.

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

## Why this project

Manually screening dozens or hundreds of resumes against a job description
is slow and inconsistent. This tool automates the first pass with a
transparent, explainable score — every ranking decision can be traced back
to specific matched or missing skills, rather than an opaque number.

## Possible extensions

- Swap the pure-Python TF-IDF for `scikit-learn`'s `TfidfVectorizer` for
  large-scale batches.
- Add semantic similarity via sentence embeddings (e.g. `sentence-transformers`)
  to catch skill synonyms TF-IDF misses.
- Persist results to a database and add a history/comparison view.
- Add authentication and multi-user support for recruiting teams.
