"""Score a resume against a job description using TF-IDF and keyword overlap."""

from __future__ import annotations

import re
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Generic posting language that should not count as skills.
_NOISE_TERMS = {
    "ability",
    "applicant",
    "candidates",
    "company",
    "description",
    "duties",
    "equal",
    "experience",
    "including",
    "job",
    "looking",
    "must",
    "need",
    "needs",
    "opportunity",
    "plus",
    "position",
    "preferred",
    "qualifications",
    "required",
    "requirements",
    "responsibilities",
    "resume",
    "role",
    "seeking",
    "skills",
    "strong",
    "team",
    "using",
    "work",
    "working",
    "years",
}

# Keep hyphenated skills (scikit-learn, tf-idf, ci/cd-style tokens with . + #).
_TOKEN_PATTERN = r"(?u)\b[a-zA-Z][a-zA-Z0-9+#.\-]{1,}\b"


def analyze_resume(resume_text: str, jd_text: str) -> dict[str, Any]:
    """Compare resume and job description.

    Returns:
        score: 0–100 match score
        matched_terms: JD keywords also present in the resume
        missing_terms: important JD keywords absent from the resume
        gaps: 3–4 concise, actionable notes
    """
    resume = (resume_text or "").strip()
    jd = (jd_text or "").strip()

    if not resume or not jd:
        return {
            "score": 0,
            "matched_terms": [],
            "missing_terms": [],
            "gaps": [
                "Provide both a resume and a job description before analysis.",
                "Upload a PDF or DOCX resume so skills and role language can be compared.",
                "Paste or upload the full job description, including required skills.",
            ],
        }

    cosine = _cosine_similarity(resume, jd)
    jd_terms = _extract_key_terms(jd)
    resume_norm = _normalize_for_match(resume)

    matched: list[str] = []
    missing: list[str] = []
    for term in jd_terms:
        if _term_in_text(term, resume_norm):
            matched.append(term)
        else:
            missing.append(term)

    overlap = (len(matched) / len(jd_terms)) if jd_terms else 0.0
    # Blend document similarity with explicit skill/keyword coverage.
    raw_score = 100.0 * (0.55 * cosine + 0.45 * overlap)
    score = int(round(min(100.0, max(0.0, raw_score))))

    return {
        "score": score,
        "matched_terms": matched[:24],
        "missing_terms": missing[:24],
        "gaps": _build_gaps(score, matched, missing, cosine),
    }


def _cosine_similarity(resume: str, jd: str) -> float:
    """TF-IDF cosine similarity between the two documents."""
    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            token_pattern=_TOKEN_PATTERN,
        )
        matrix = vectorizer.fit_transform([resume, jd])
        if matrix.shape[1] == 0:
            return 0.0
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except ValueError:
        return 0.0


def _extract_key_terms(jd: str, limit: int = 28) -> list[str]:
    """Rank job-description terms with TF-IDF and keep distinctive phrases."""
    try:
        # Unigrams only (hyphenated tools stay intact). Adjacent bigrams
        # from sentences ("need python") are too noisy for a skills list.
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 1),
            min_df=1,
            max_features=80,
            token_pattern=_TOKEN_PATTERN,
        )
        matrix = vectorizer.fit_transform([jd])
    except ValueError:
        return []

    features = vectorizer.get_feature_names_out()
    weights = matrix.toarray()[0]
    ranked = sorted(zip(features, weights), key=lambda item: item[1], reverse=True)

    terms: list[str] = []
    seen: set[str] = set()
    for term, weight in ranked:
        if weight <= 0:
            continue
        cleaned = term.strip().lower()
        if not _is_useful_term(cleaned) or cleaned in seen:
            continue
        # Prefer longer phrases; skip fragments already covered.
        if any(_covers(existing, cleaned) for existing in terms):
            continue
        seen.add(cleaned)
        terms.append(cleaned)
        if len(terms) >= limit:
            break
    return _dedupe_nested(terms)


def _is_useful_term(term: str) -> bool:
    words = term.split()
    if any(word in _NOISE_TERMS for word in words):
        return False
    if all(len(word.replace("-", "")) < 3 for word in words):
        return False
    if re.fullmatch(r"[\d.\-]+", term.replace(" ", "")):
        return False
    return True


def _covers(kept: str, candidate: str) -> bool:
    """True if candidate is already represented by a kept phrase."""
    if candidate == kept:
        return True
    kept_parts = set(kept.replace("-", " ").split())
    cand_parts = set(candidate.replace("-", " ").split())
    if cand_parts and cand_parts.issubset(kept_parts) and candidate != kept:
        return True
    return False


def _dedupe_nested(terms: list[str]) -> list[str]:
    """Drop short terms fully contained in a longer selected phrase."""
    ordered = sorted(terms, key=lambda t: (-len(t), t))
    kept: list[str] = []
    for term in ordered:
        if any(_covers(existing, term) for existing in kept):
            continue
        kept.append(term)
    # Restore original importance order.
    rank = {term: i for i, term in enumerate(terms)}
    return sorted(kept, key=lambda t: rank.get(t, 0))


def _normalize_for_match(text: str) -> str:
    return " ".join(re.findall(_TOKEN_PATTERN, text.lower()))


def _term_in_text(term: str, normalized_text: str) -> bool:
    """True if the phrase appears, allowing hyphen and simple plural variants."""
    collapsed = normalized_text.replace("-", " ")
    base = term.replace("-", " ").strip()
    variants = {term, base}
    if base.endswith("s") and len(base) > 4:
        variants.add(base[:-1])
    else:
        variants.add(base + "s")

    for variant in variants:
        parts = variant.replace("-", " ").split()
        if not parts:
            continue
        core = r"[\s\-]+".join(re.escape(part) for part in parts)
        pattern = rf"\b{core}\b"
        if re.search(pattern, normalized_text) or re.search(pattern, collapsed):
            return True
    return False


def _build_gaps(
    score: int,
    matched: list[str],
    missing: list[str],
    cosine: float,
) -> list[str]:
    """Turn score and term overlap into a short, actionable critique."""
    gaps: list[str] = []

    if missing:
        preview = ", ".join(missing[:5])
        gaps.append(
            f"The resume does not clearly cover these job-description terms: {preview}. "
            "Add them in the skills list or recent role bullets if the experience is real."
        )
    else:
        gaps.append(
            "Keyword coverage is strong. Tighten phrasing so the same tools and methods "
            "appear in both the skills section and the most recent role."
        )

    if score < 55:
        gaps.append(
            "Overall match is low. Rewrite summary and recent bullets using the job "
            "description's wording for required tools, domain, and outcomes."
        )
    elif score < 75:
        gaps.append(
            "Partial alignment. Promote the overlapping strengths higher in the resume "
            "and drop generic duties that do not map to this role."
        )
    else:
        gaps.append(
            "The resume already tracks this posting well. Lead with the matched skills "
            "and keep remaining bullets specific to this job family."
        )

    if cosine < 0.25:
        gaps.append(
            "Document language diverges from the posting. Mirror section headings and "
            "responsibility verbs from the job description where they match your work."
        )
    elif len(missing) >= 8:
        gaps.append(
            "Several required capabilities are still absent. Prioritize the most repeated "
            "tools and methods from the posting rather than adding unrelated extras."
        )
    else:
        gaps.append(
            "Quantify impact (scale, time saved, quality, revenue, or users) next to the "
            "matched skills so a reviewer can map your results to the role."
        )

    if len(matched) < 5 and len(gaps) < 4:
        gaps.append(
            "Too few shared keywords. Spell out technologies, methods, and domain terms "
            "instead of relying on generic statements about teamwork or communication."
        )

    return gaps[:4]
