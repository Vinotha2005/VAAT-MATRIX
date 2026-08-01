import re
from collections import Counter
from typing import Dict, List

try:
    import spacy
except Exception:
    spacy = None

from app.services.ai_service import summarize_text

STOP_WORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "have", "been", "will",
    "about", "their", "these", "those", "what", "when", "where", "which", "while", "than",
    "can", "also", "your", "using", "used", "more", "through", "study", "chapter",
    "topic", "topics", "pdf", "document", "lesson", "lecture", "file", "dummy", "sample",
    "unit", "type", "types", "grammar", "non", "terminal", "terminals"
}


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


_SPACY_NLP = None


def _get_spacy_nlp():
    global _SPACY_NLP
    if spacy is None:
        return None
    if _SPACY_NLP is not None:
        return _SPACY_NLP
    try:
        _SPACY_NLP = spacy.load("en_core_web_sm")
    except Exception:
        return None
    return _SPACY_NLP


def _extract_topics(text: str, limit: int = 6) -> List[str]:
    nlp = _get_spacy_nlp()
    if nlp is not None:
        doc = nlp(text)
        phrase_scores: Counter = Counter()
        token_scores: Counter = Counter()

        for chunk in doc.noun_chunks:
            phrase = " ".join(token.lemma_.lower() for token in chunk if token.is_alpha and not token.is_stop)
            if len(phrase.split()) >= 2 and phrase:
                phrase_scores[phrase] += 1

        for ent in doc.ents:
            label_text = ent.text.lower().strip()
            if label_text:
                phrase_scores[label_text] += 2

        for token in doc:
            t = token.lemma_.lower()
            if token.is_alpha and not token.is_stop and len(t) > 2 and t not in STOP_WORDS:
                token_scores[t] += 1

        topics: List[str] = []
        for phrase, _ in phrase_scores.most_common():
            if phrase not in topics:
                topics.append(phrase)
            if len(topics) >= limit:
                return topics
        for token, _ in token_scores.most_common():
            if token not in topics:
                topics.append(token)
            if len(topics) >= limit:
                break
        if topics:
            return topics

    normalized = _normalize(text)
    tokens = [token for token in normalized.split() if len(token) > 2 and token not in STOP_WORDS]
    if not tokens:
        return []

    token_counts = Counter(tokens)
    phrase_counts = Counter()
    for index in range(len(tokens) - 1):
        phrase = f"{tokens[index]} {tokens[index + 1]}"
        phrase_counts[phrase] += 1

    topics = []
    for phrase, _ in phrase_counts.most_common():
        if phrase not in topics:
            topics.append(phrase)
        if len(topics) >= limit:
            return topics

    for token, _ in token_counts.most_common():
        if token not in topics:
            topics.append(token)
        if len(topics) >= limit:
            break

    return topics


def _make_options(primary: str, topics: List[str]) -> List[str]:
    options = [primary.title()]
    for topic in topics:
        title = topic.title()
        if title not in options:
            options.append(title)
        if len(options) == 4:
            break
    while len(options) < 4:
        options.append("General Study Notes")
    return options[:4]


def _question_bank_from_text(text: str) -> List[Dict]:
    topics = _extract_topics(text)
    summary = summarize_text(text).get("summary", "")
    primary = topics[0] if topics else "the document"
    secondary = topics[1] if len(topics) > 1 else primary
    tertiary = topics[2] if len(topics) > 2 else secondary
    options = _make_options(primary, topics[1:])

    mcq_answer = options[0]
    true_statement = f"The document discusses {primary}."
    false_statement = f"The document is mainly about {tertiary if tertiary != primary else 'sports'}."
    fill_answer = primary.title()
    short_answer = summary if summary else f"The document focuses on {primary}."

    return [
        {
            "id": "mcq1",
            "type": "mcq",
            "question": "Which topic is the document mainly focused on?",
            "options": options,
            "answer": mcq_answer,
            "explanation": f"The extracted content repeatedly points to {primary} as the main topic.",
        },
        {
            "id": "tf1",
            "type": "true_false",
            "question": true_statement,
            "answer": True,
            "explanation": f"The summary and extracted text clearly mention {primary}.",
        },
        {
            "id": "fill1",
            "type": "fill_blank",
            "question": f"The document mainly focuses on ______ and related ideas.",
            "answer": fill_answer,
            "acceptable_answers": [fill_answer.lower(), primary.lower()],
            "explanation": f"A strong keyword from the document is {primary}.",
        },
        {
            "id": "short1",
            "type": "short_answer",
            "question": "Write one or two sentences explaining the main idea of the PDF.",
            "answer": short_answer,
            "keywords": [topic for topic in [primary, secondary, tertiary] if topic],
            "explanation": "The model answer is based on the generated summary and the strongest extracted topics.",
        },
    ]


def generate_quiz(text: str) -> Dict[str, List[Dict]]:
    return {"questions": _question_bank_from_text(text)}


def grade_short_answer(user_answer: str, expected_keywords: List[str]) -> bool:
    normalized = _normalize(user_answer)
    matches = 0
    for keyword in expected_keywords:
        keyword_normalized = _normalize(keyword)
        if keyword_normalized and keyword_normalized in normalized:
            matches += 1
    return matches >= max(1, min(2, len(expected_keywords)))
