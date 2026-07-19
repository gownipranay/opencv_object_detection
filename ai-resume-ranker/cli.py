#!/usr/bin/env python3
"""Command-line interface: rank resumes in a folder against a job description.

Usage:
    python cli.py --job sample_data/job_description.txt --resumes sample_data/resumes
"""
import argparse
from pathlib import Path

from resume_ranker import extract_text, rank_resumes


def load_resumes(folder: Path) -> dict:
    resumes = {}
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix.lower() in {".txt", ".pdf", ".docx"}:
            resumes[path.name] = extract_text(path)
    return resumes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, help="Path to job description file")
    parser.add_argument("--resumes", required=True, help="Folder of resume files")
    parser.add_argument("--top", type=int, default=None, help="Only show top N results")
    args = parser.parse_args()

    job_description = extract_text(Path(args.job))
    resumes = load_resumes(Path(args.resumes))

    if not resumes:
        raise SystemExit(f"No .txt/.pdf/.docx resumes found in {args.resumes}")

    ranked = rank_resumes(job_description, resumes)
    if args.top:
        ranked = ranked[: args.top]

    print(f"\nRanked {len(ranked)} resume(s) against '{args.job}':\n")
    for i, result in enumerate(ranked, start=1):
        d = result.as_dict()
        print(f"{i}. {d['name']}  —  match score: {d['score']}%")
        print(f"   text similarity: {d['text_similarity']}%   skill coverage: {d['skill_score']}%")
        print(f"   matched skills: {', '.join(d['matched_skills']) or '(none)'}")
        if d["missing_skills"]:
            print(f"   missing skills: {', '.join(d['missing_skills'])}")
        print()


if __name__ == "__main__":
    main()
