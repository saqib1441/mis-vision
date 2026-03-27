import re


def normalize_name(name: str) -> str:
    name = re.sub(r"[_=.\-]+", " ", name)
    words = [word.capitalize() for word in name.split() if word.strip()]
    return " ".join(words)


def slugify_name(name: str) -> str:
    name = re.sub(r"[_=.\-]+", " ", name)
    words = [word.lower() for word in name.split() if word.strip()]
    return "-".join(words)
