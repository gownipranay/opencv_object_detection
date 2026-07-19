"""Core ranking logic: score resumes against a job description."""
from dataclasses import dataclass, field

from .skills import skill_overlap
from .tfidf import (
    build_vocabulary,
    compute_idf,
    cosine_similarity,
    tfidf_vector,
    tokenize,
)

# Weight given to keyword/skill overlap vs. overall TF-IDF text similarity.
SKILL_WEIGHT = 0.6
TEXT_WEIGHT = 0.4


@dataclass
class RankedResume:
    name: str
    score: float
    text_similarity: float
    skill_score: float
    matched_skills: set = field(default_factory=set)
    missing_skills: set = field(default_factory=set)

    def as_dict(self):
        return {
            "name": self.name,
            "score": round(self.score * 100, 1),
            "text_similarity": round(self.text_similarity * 100, 1),
            "skill_score": round(self.skill_score * 100, 1),
            "matched_skills": sorted(self.matched_skills),
            "missing_skills": sorted(self.missing_skills),
        }


def _skill_score(matched: set, job_skill_count: int) -> float:
    if job_skill_count == 0:
        return 1.0
    return len(matched) / job_skill_count


def rank_resumes(job_description: str, resumes: dict) -> list:
    """Rank resumes against a job description.

    Args:
        job_description: raw text of the job posting.
        resumes: mapping of {resume_name: resume_text}.

    Returns:
        List of RankedResume, sorted best-match first.
    """
    job_tokens = tokenize(job_description)
    resume_names = list(resumes.keys())
    resume_token_lists = [tokenize(resumes[name]) for name in resume_names]

    vocab = build_vocabulary([job_tokens] + resume_token_lists)
    idf = compute_idf([job_tokens] + resume_token_lists, vocab)
    job_vector = tfidf_vector(job_tokens, vocab, idf)

    job_skills = None
    results = []
    for name, tokens in zip(resume_names, resume_token_lists):
        resume_vector = tfidf_vector(tokens, vocab, idf)
        text_similarity = cosine_similarity(job_vector, resume_vector)

        matched, missing = skill_overlap(job_description, resumes[name])
        if job_skills is None:
            job_skills = matched | missing
        skill_score = _skill_score(matched, len(job_skills) if job_skills else 0)

        combined = TEXT_WEIGHT * text_similarity + SKILL_WEIGHT * skill_score
        results.append(
            RankedResume(
                name=name,
                score=combined,
                text_similarity=text_similarity,
                skill_score=skill_score,
                matched_skills=matched,
                missing_skills=missing,
            )
        )

    results.sort(key=lambda r: r.score, reverse=True)
    return results
