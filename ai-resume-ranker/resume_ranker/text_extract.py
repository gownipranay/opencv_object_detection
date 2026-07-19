"""Extract raw text from resume files (.txt, .pdf, .docx).

PDF/DOCX support is optional: if the corresponding library isn't installed,
a clear error is raised only when that file type is actually used, so
plain-text resumes work with zero extra dependencies.
"""
from pathlib import Path


def extract_text(file_path) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ImportError(
                "Reading .pdf resumes requires the 'pypdf' package. "
                "Install it with: pip install pypdf"
            ) from exc
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if suffix == ".docx":
        try:
            import docx
        except ImportError as exc:
            raise ImportError(
                "Reading .docx resumes requires the 'python-docx' package. "
                "Install it with: pip install python-docx"
            ) from exc
        document = docx.Document(str(path))
        return "\n".join(p.text for p in document.paragraphs)

    raise ValueError(
        f"Unsupported resume file type: '{suffix}'. Use .txt, .pdf, or .docx."
    )
