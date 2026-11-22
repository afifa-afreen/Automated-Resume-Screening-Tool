"""Core functions for the Automated Resume Screening Tool."""

from pathlib import Path
import re
from typing import Iterable

import numpy as np
import pandas as pd
import pdfplumber
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# This is an editable demonstration vocabulary, not a complete skills ontology.
DEFAULT_SKILLS = [
    "python", "sql", "pandas", "numpy", "machine learning",
    "scikit-learn", "flask", "django", "fastapi", "rest api",
    "git", "excel", "power bi", "tableau", "data visualization",
    "java", "javascript", "react", "node.js", "mongodb",
    "postgresql", "aws", "docker", "linux", "statistics"
]


def extract_text(file_path: str | Path) -> str:
    """Extract text from PDF, DOCX, or TXT. Scanned PDFs need OCR, not included here."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        pages = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        return "\n".join(pages)

    if suffix == ".docx":
        document = Document(path)
        paragraphs = [p.text for p in document.paragraphs]
        # Also read simple tables, which often contain resume details.
        for table in document.tables:
            for row in table.rows:
                paragraphs.append(" ".join(cell.text for cell in row.cells))
        return "\n".join(paragraphs)

    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")

    raise ValueError(f"Unsupported file type: {suffix}")


def clean_text(text: str) -> str:
    """Normalize whitespace and lowercase text while preserving useful punctuation."""
    text = text.lower()
    text = re.sub(r"[\r\t]+", " ", text)
    text = re.sub(r"[^a-z0-9+#./\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_skill(skill: str) -> str:
    return clean_text(skill)


def extract_skills(text: str, skills: Iterable[str] = DEFAULT_SKILLS) -> list[str]:
    """Find skills using case-insensitive whole-phrase matching."""
    normalized = clean_text(text)
    found = []

    for skill in skills:
        candidate = normalize_skill(skill)
        if not candidate:
            continue

        # Boundaries avoid matching 'java' inside 'javascript'.
        pattern = rf"(?<![a-z0-9]){re.escape(candidate)}(?![a-z0-9])"
        if re.search(pattern, normalized):
            found.append(skill)

    return sorted(set(found), key=str.lower)


def calculate_similarity(resume_text: str, job_text: str) -> float:
    """Return TF-IDF cosine similarity as a percentage from 0 to 100."""
    documents = [clean_text(resume_text), clean_text(job_text)]
    if not any(documents):
        return 0.0

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    try:
        matrix = vectorizer.fit_transform(documents)
    except ValueError:  # Both documents may contain only stop words or be empty.
        return 0.0

    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return round(float(score) * 100, 2)


def score_resume(
    resume_text: str,
    job_text: str,
    required_skills: list[str],
    similarity_weight: float = 0.60,
    skill_weight: float = 0.40,
) -> dict:
    """Combine text similarity and required-skill coverage into an explainable score."""
    if not np.isclose(similarity_weight + skill_weight, 1.0):
        raise ValueError("similarity_weight + skill_weight must equal 1.0")

    detected = extract_skills(resume_text, required_skills)
    required_normalized = {normalize_skill(s) for s in required_skills}
    detected_normalized = {normalize_skill(s) for s in detected}

    coverage = (
        len(detected_normalized & required_normalized) / len(required_normalized) * 100
        if required_normalized else 0.0
    )
    similarity = calculate_similarity(resume_text, job_text)
    final_score = similarity * similarity_weight + coverage * skill_weight

    missing = [
        skill for skill in required_skills
        if normalize_skill(skill) not in detected_normalized
    ]

    return {
        "similarity_score": round(similarity, 2),
        "skill_coverage": round(coverage, 2),
        "matching_score": round(final_score, 2),
        "detected_skills": ", ".join(detected),
        "missing_required_skills": ", ".join(missing),
    }


def screen_resumes(
    resume_dir: str | Path,
    job_description: str,
    required_skills: list[str],
    review_threshold: float = 50.0,
) -> pd.DataFrame:
    """Process all supported files and return a ranked results DataFrame."""
    folder = Path(resume_dir)
    if not folder.exists():
        raise FileNotFoundError(f"Resume folder not found: {folder}")

    results = []
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            raw_text = extract_text(path)
            if not raw_text.strip():
                results.append({
                    "candidate_file": path.name,
                    "status": "Needs manual review: no text extracted",
                    "matching_score": 0.0,
                    "similarity_score": 0.0,
                    "skill_coverage": 0.0,
                    "detected_skills": "",
                    "missing_required_skills": ", ".join(required_skills),
                })
                continue

            metrics = score_resume(raw_text, job_description, required_skills)
            metrics["candidate_file"] = path.name
            metrics["status"] = (
                "Prioritize for human review"
                if metrics["matching_score"] >= review_threshold
                else "Further review required"
            )
            results.append(metrics)

        except Exception as exc:
            results.append({
                "candidate_file": path.name,
                "status": f"Processing error: {exc}",
                "matching_score": 0.0,
                "similarity_score": 0.0,
                "skill_coverage": 0.0,
                "detected_skills": "",
                "missing_required_skills": ", ".join(required_skills),
            })

    columns = [
        "candidate_file", "matching_score", "similarity_score",
        "skill_coverage", "detected_skills", "missing_required_skills", "status"
    ]
    dataframe = pd.DataFrame(results, columns=columns)
    if not dataframe.empty:
        dataframe = dataframe.sort_values(
            "matching_score", ascending=False
        ).reset_index(drop=True)
        dataframe.insert(0, "rank", range(1, len(dataframe) + 1))
    return dataframe


def save_report(dataframe: pd.DataFrame, output_path: str | Path) -> Path:
    """Save screening results to CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False, encoding="utf-8")
    return path
