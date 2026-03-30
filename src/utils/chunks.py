import re
from typing import List
from num2words import num2words

from src.utils.constants import ModelType

TURBO_PARALINGUISTIC_TAGS = [
    "laugh",
    "chuckle",
    "sigh",
    "gasp",
    "cough",
    "clear throat",
    "sniff",
    "groan",
    "shush",
]


def text_to_chunks(text: str, model_type: ModelType, max_chars: int = 500) -> List[str]:
    all_tags = re.findall(r"\[(.*?)\]", text)
    valid_tags_found = []

    if model_type == ModelType.TURBO_MODEL:
        for i, tag_content in enumerate(all_tags):
            clean_tag = tag_content.strip().lower()
            if clean_tag in TURBO_PARALINGUISTIC_TAGS:
                placeholder = f"__TAG_{len(valid_tags_found)}__"
                text = text.replace(f"[{tag_content}]", placeholder)
                valid_tags_found.append(f"[{clean_tag}]")
            else:
                text = text.replace(f"[{tag_content}]", "")
    else:
        text = re.sub(r"\[.*?\]", "", text)

    def replace_decimal(match):
        parts = match.group(0).split(".")
        whole = num2words(int(parts[0]))
        decimal_digits = " ".join([num2words(int(d)) for d in parts[1]])
        return f"{whole} point {decimal_digits}"

    processed = re.sub(r"\d+\.\d+", replace_decimal, text)

    processed = re.sub(
        r"(\d+)(st|nd|rd|th)",
        lambda m: num2words(int(m.group(1)), to="ordinal"),
        processed,
    )

    processed = re.sub(
        r"\b\d{4}\b", lambda m: num2words(int(m.group(0)), to="year"), processed
    )

    processed = re.sub(r"\b\d+\b", lambda m: num2words(int(m.group(0))), processed)

    processed = re.sub(r"\s+", " ", processed).strip()

    for i, tag in enumerate(valid_tags_found):
        processed = processed.replace(f"__TAG_{i}__", tag)

    chunks = []
    while len(processed) > 0:
        if len(processed) <= max_chars:
            chunks.append(processed)
            break

        limit = processed[:max_chars]
        split_at = max(limit.rfind(". "), limit.rfind("! "), limit.rfind("? "))

        if split_at == -1:
            split_at = limit.rfind(" ")
            if split_at == -1:
                split_at = max_chars

        chunks.append(processed[: split_at + 1].strip())
        processed = processed[split_at + 1 :].strip()

    return [c for c in chunks if c]
