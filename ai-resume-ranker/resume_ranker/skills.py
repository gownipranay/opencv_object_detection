"""A curated skill/keyword taxonomy used for explainable skill matching.

TF-IDF similarity alone doesn't tell a recruiter *which* skills matched.
This module extracts a normalized set of known skills from free text so
the ranker can report overlap and gaps explicitly.
"""
import re

SKILL_TAXONOMY = {
    "python", "java", "c++", "c#", "javascript", "typescript", "go", "rust",
    "sql", "r", "matlab", "scala", "kotlin", "swift", "php", "ruby",
    "html", "css", "react", "angular", "vue", "node.js", "django", "flask",
    "fastapi", "spring", "express",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data science", "data engineering", "data analysis", "statistics",
    "tensorflow", "pytorch", "keras", "scikit-learn", "opencv", "pandas",
    "numpy", "spacy", "hugging face", "transformers", "llm", "genai",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "linux",
    "ci/cd", "git", "github", "rest api", "graphql", "microservices",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "spark",
    "hadoop", "airflow", "kafka", "tableau", "power bi", "excel",
    "agile", "scrum", "project management", "communication", "leadership",
    "problem solving", "teamwork",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills(text: str) -> set:
    """Return the subset of the taxonomy present in `text`."""
    normalized = normalize(text)
    found = set()
    for skill in SKILL_TAXONOMY:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, normalized):
            found.add(skill)
    return found


def skill_overlap(job_text: str, resume_text: str):
    """Return (matched, missing) skill sets for a resume vs. a job posting."""
    job_skills = extract_skills(job_text)
    resume_skills = extract_skills(resume_text)
    matched = job_skills & resume_skills
    missing = job_skills - resume_skills
    return matched, missing
