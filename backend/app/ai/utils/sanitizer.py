"""Input sanitisation and prompt-injection protection."""

import re
from typing import Any

# Patterns indicative of prompt injection / jailbreak attempts
_INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"ignore\s+(all\s+)?(previous|above|below)\s+instructions", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?(previous|above|below)", re.IGNORECASE),
    re.compile(r"system\s+prompt", re.IGNORECASE),
    re.compile(r"you\s+are\s+(now|not\s+required\s+to)", re.IGNORECASE),
    re.compile(r"act\s+as\s+(if|though)", re.IGNORECASE),
    re.compile(r"role.?play", re.IGNORECASE),
    re.compile(r"do\s+not\s+follow", re.IGNORECASE),
    re.compile(r"disregard", re.IGNORECASE),
    re.compile(r"output\s+in\s+json", re.IGNORECASE),
    re.compile(r"<[^>]*>", re.IGNORECASE),  # HTML/XML tags
]


def is_prompt_injection(text: str) -> bool:
    """Return True if the input matches prompt-injection patterns."""
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            return True
    return False


def sanitize_input(text: str, max_length: int = 4000) -> str:
    """Trim and strip dangerous characters from user input."""
    text = text.strip()[:max_length]
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text


def validate_uploaded_file(filename: str, content: bytes,
                           max_size_mb: int = 10) -> tuple[bool, str]:
    """Validate an uploaded document file."""
    allowed_extensions = {".pdf", ".docx", ".txt", ".md", ".csv"}
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in allowed_extensions:
        return False, f"File type '{ext}' is not supported. Allowed: {', '.join(allowed_extensions)}"
    max_bytes = max_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        return False, f"File exceeds {max_size_mb} MB limit"
    return True, ""
