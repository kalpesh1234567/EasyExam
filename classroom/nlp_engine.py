"""
NLP Evaluation Engine for Subjective Answer Evaluation
Uses TF-IDF + Cosine Similarity + Keyword Matching
"""
import re
import math
from collections import Counter


# ---------- Text Preprocessing ----------

STOPWORDS = {
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'shall', 'can', 'need', 'dare', 'ought',
    'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
    'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'between', 'out', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either',
    'neither', 'not', 'only', 'own', 'same', 'than', 'too', 'very', 'just',
    'it', 'its', 'this', 'that', 'these', 'those', 'i', 'me', 'my', 'we',
    'our', 'you', 'your', 'he', 'his', 'she', 'her', 'they', 'their',
    'what', 'which', 'who', 'whom', 'when', 'where', 'why', 'how',
    'all', 'each', 'every', 'any', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'up', 'about', 'also', 'like',
}

SUFFIXES = ['ing', 'tion', 'sion', 'ed', 'er', 'est', 'ly', 'ment', 'ness',
            'ity', 'ies', 'es', 'al', 'ous', 'ive', 'ful', 'less', 'able', 'ible']


def stem(word):
    """Simple rule-based stemmer."""
    word = word.lower()
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[:-len(suffix)]
    return word


def tokenize(text):
    """Lowercase, remove punctuation, split into tokens."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = text.split()
    return tokens


def preprocess(text, remove_stopwords=True, apply_stem=True):
    """Full preprocessing pipeline."""
    tokens = tokenize(text)
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    if apply_stem:
        tokens = [stem(t) for t in tokens]
    return tokens


# ---------- TF-IDF Vectorizer ----------

def compute_tf(tokens):
    """Term Frequency."""
    count = Counter(tokens)
    total = len(tokens) if tokens else 1
    return {word: freq / total for word, freq in count.items()}


def compute_idf(documents):
    """Inverse Document Frequency across a list of token lists."""
    N = len(documents)
    idf = {}
    all_words = set(word for doc in documents for word in doc)
    for word in all_words:
        containing = sum(1 for doc in documents if word in doc)
        idf[word] = math.log((N + 1) / (containing + 1)) + 1
    return idf


def tfidf_vector(tokens, idf):
    """Build TF-IDF vector."""
    tf = compute_tf(tokens)
    return {word: tf_val * idf.get(word, 1) for word, tf_val in tf.items()}


# ---------- Cosine Similarity ----------

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two TF-IDF vectors."""
    if not vec1 or not vec2:
        return 0.0
    all_words = set(vec1) | set(vec2)
    dot = sum(vec1.get(w, 0) * vec2.get(w, 0) for w in all_words)
    mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


# ---------- Keyword Matching ----------

def extract_keywords(text, top_n=15):
    """Extract important keywords using TF scoring (no IDF, single doc)."""
    tokens = preprocess(text, remove_stopwords=True, apply_stem=False)
    count = Counter(tokens)
    # Return top N by frequency
    return [word for word, _ in count.most_common(top_n)]


def keyword_overlap_score(student_tokens, reference_keywords):
    """What fraction of reference keywords appear in the student answer."""
    if not reference_keywords:
        return 0.0
    student_set = set(student_tokens)
    ref_set = set(stem(k) for k in reference_keywords)
    matched = sum(1 for k in ref_set if any(stem(s) == k for s in student_set))
    return matched / len(ref_set)


# ---------- Length & Coverage Score ----------

def length_score(student_text, reference_text):
    """Reward answers of reasonable length relative to reference."""
    s_len = len(student_text.split())
    r_len = len(reference_text.split())
    if r_len == 0:
        return 0.5
    ratio = s_len / r_len
    # Ideal ratio is 0.5–1.5x reference length
    if 0.5 <= ratio <= 1.5:
        return 1.0
    elif ratio < 0.5:
        return max(0.3, ratio / 0.5)
    else:
        return max(0.5, 1.5 / ratio)


# ---------- Main Evaluation Function ----------

def evaluate_answer(student_answer: str, reference_answer: str, max_score: int = 10) -> dict:
    """
    Evaluate a student's subjective answer against a reference answer.

    Returns a dict with:
        - score (float): calculated score out of max_score
        - percentage (float): 0–100
        - similarity (float): cosine similarity 0–1
        - keyword_coverage (float): fraction of keywords covered 0–1
        - feedback (str): detailed feedback text
        - matched_keywords (list): keywords student got right
        - missed_keywords (list): keywords student missed
    """
    if not student_answer or not student_answer.strip():
        return {
            'score': 0,
            'percentage': 0,
            'similarity': 0,
            'keyword_coverage': 0,
            'feedback': 'No answer provided.',
            'matched_keywords': [],
            'missed_keywords': [],
        }

    # Preprocess
    student_tokens = preprocess(student_answer)
    reference_tokens = preprocess(reference_answer)

    # Build TF-IDF
    documents = [student_tokens, reference_tokens]
    idf = compute_idf(documents)
    student_vec = tfidf_vector(student_tokens, idf)
    reference_vec = tfidf_vector(reference_tokens, idf)

    # 1. Cosine Similarity (weight: 50%)
    cos_sim = cosine_similarity(student_vec, reference_vec)

    # 2. Keyword Coverage (weight: 35%)
    ref_keywords = extract_keywords(reference_answer, top_n=12)
    student_raw_tokens = preprocess(student_answer, remove_stopwords=True, apply_stem=False)

    matched_kws = []
    missed_kws = []
    for kw in ref_keywords:
        kw_stem = stem(kw)
        if any(stem(s) == kw_stem for s in student_raw_tokens):
            matched_kws.append(kw)
        else:
            missed_kws.append(kw)

    kw_coverage = len(matched_kws) / len(ref_keywords) if ref_keywords else 0

    # 3. Length Score (weight: 15%)
    len_score = length_score(student_answer, reference_answer)

    # Weighted Final Score
    final_fraction = (cos_sim * 0.50) + (kw_coverage * 0.35) + (len_score * 0.15)
    score = round(final_fraction * max_score, 2)
    percentage = round(final_fraction * 100, 1)

    # Feedback generation
    feedback = _generate_feedback(cos_sim, kw_coverage, len_score, matched_kws, missed_kws)

    return {
        'score': score,
        'percentage': percentage,
        'similarity': round(cos_sim, 3),
        'keyword_coverage': round(kw_coverage, 3),
        'length_score': round(len_score, 3),
        'feedback': feedback,
        'matched_keywords': matched_kws[:8],
        'missed_keywords': missed_kws[:8],
    }


def _generate_feedback(cos_sim, kw_coverage, len_score, matched_kws, missed_kws):
    lines = []

    # Semantic similarity
    if cos_sim >= 0.75:
        lines.append("✅ Excellent semantic alignment with the reference answer.")
    elif cos_sim >= 0.5:
        lines.append("🔵 Good conceptual understanding shown.")
    elif cos_sim >= 0.3:
        lines.append("🟡 Partial understanding demonstrated.")
    else:
        lines.append("🔴 Answer needs significant improvement in content.")

    # Keyword coverage
    if kw_coverage >= 0.75:
        lines.append("✅ Most key concepts are covered.")
    elif kw_coverage >= 0.5:
        lines.append("🔵 Several key concepts mentioned.")
    elif kw_coverage >= 0.25:
        lines.append("🟡 Some important concepts are missing.")
    else:
        lines.append("🔴 Many key concepts are absent.")

    if matched_kws:
        lines.append(f"✔ Keywords covered: {', '.join(matched_kws[:6])}")
    if missed_kws:
        lines.append(f"✘ Consider including: {', '.join(missed_kws[:6])}")

    # Length
    if len_score >= 0.9:
        lines.append("✅ Answer length is appropriate.")
    elif len_score < 0.5:
        lines.append("⚠ Answer is too short — add more detail.")

    return "\n".join(lines)


# ---------- Batch Evaluation ----------

def evaluate_submission(answers_data: list) -> dict:
    """
    Evaluate a full test submission.
    answers_data: list of {'student_answer': str, 'reference_answer': str, 'max_score': int}
    Returns: {'total_score': float, 'results': list of individual results}
    """
    results = []
    total = 0
    for item in answers_data:
        result = evaluate_answer(
            item['student_answer'],
            item['reference_answer'],
            item.get('max_score', 10)
        )
        results.append(result)
        total += result['score']
    return {'total_score': round(total, 2), 'results': results}
