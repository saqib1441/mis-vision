import re
import unicodedata


def sanitize_tts_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)

    text = "".join(
        ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in "\n\r\t"
    )

    text = re.sub(r"[\n\r\t]+", " ", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text
