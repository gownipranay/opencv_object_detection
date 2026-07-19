import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resume_ranker import extract_text, rank_resumes

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def load_sample_resumes():
    resumes_dir = SAMPLE_DIR / "resumes"
    return {p.name: extract_text(p) for p in sorted(resumes_dir.iterdir())}


def test_ml_engineer_job_ranks_alice_first():
    job_description = extract_text(SAMPLE_DIR / "job_description.txt")
    resumes = load_sample_resumes()

    ranked = rank_resumes(job_description, resumes)
    names = [r.name for r in ranked]

    assert names[0] == "alice_johnson.txt"
    assert names[-1] == "bob_smith.txt"


def test_scores_are_sorted_descending():
    job_description = extract_text(SAMPLE_DIR / "job_description.txt")
    resumes = load_sample_resumes()
    ranked = rank_resumes(job_description, resumes)
    scores = [r.score for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_matched_skills_are_reported_for_top_candidate():
    job_description = extract_text(SAMPLE_DIR / "job_description.txt")
    resumes = load_sample_resumes()
    ranked = rank_resumes(job_description, resumes)
    top = ranked[0]
    assert "python" in top.matched_skills
    assert "pytorch" in top.matched_skills or "tensorflow" in top.matched_skills
