import re
from typing import List

def segment_clauses(text: str, min_words: int = 10, max_words: int = 150) -> List[str]:
    """
    Improved clause segmentation that supports:
    - Numbered clauses (1., 2., A., (a), etc.)
    - Legal-style headings (e.g., 'Confidentiality', 'Termination', etc.)
    """

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Split on heading-style lines (Capitalized words)
    heading_pattern = r'(?:(?<=\n)|^)([A-Z][A-Za-z ]{3,60})(?=\n|:)'

    # Apply heading split first
    parts = re.split(heading_pattern, text)

    clauses = []

    # If headings detected, pair as (Title + Body)
    if len(parts) > 1:
        for i in range(1, len(parts), 2):
            title = parts[i].strip()
            body = parts[i+1].strip()
            if len(body.split()) >= min_words:
                clauses.append(f"{title}: {body}")
    else:
        # Fallback to numbered/structured patterns and paragraph breaks
        patterns = [
            r'\n\s*\d+\.\s+',
            r'\n\s*\(\d+\)\s+',
            r'\n\s*[A-Z]\.\s+',
            r'\n\s*\([a-z]\)\s+',
            r'\n\s*Article\s+\d+',
            r'\n\s*Section\s+\d+',
            r'\n\s*Clause\s+\d+',
            r'\n\n+',
        ]
        combined_pattern = '|'.join(patterns)
        clauses = re.split(combined_pattern, text)

    # Clean + word filtering; split overly long clauses by sentences
    cleaned_clauses: List[str] = []
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
        words = clause.split()
        wc = len(words)
        if wc < min_words:
            continue
        if wc > max_words:
            sentences = re.split(r'(?<=[.!?])\s+', clause)
            current = ""
            for s in sentences:
                test = (current + " " + s).strip() if current else s
                if len(test.split()) <= max_words:
                    current = test
                else:
                    if current:
                        cleaned_clauses.append(current.strip())
                    current = s
            if current:
                cleaned_clauses.append(current.strip())
        else:
            cleaned_clauses.append(clause)

    # Remove duplicates while preserving order
    seen = set()
    final_clauses: List[str] = []
    for c in cleaned_clauses:
        if c not in seen:
            seen.add(c)
            final_clauses.append(c)

    return final_clauses
