import re

from click import prompt

class GuardrailService:

    def check_prompt_injection(self, prompt: str) -> bool:
        suspicious_patterns = [
            "ignore previous instructions",
            "ignore all previous instructions",
            "forget previous instructions",
            "system prompt",
            "reveal your instructions",
            "show me your prompt",
            "ignore the document",
        ]

        prompt_lower = prompt.lower()

        for pattern in suspicious_patterns:
            if pattern in prompt_lower:
                return True

        return False

    def redact_secrets(self, text: str) -> str:

        secret_patterns = [
            r"sk-[a-zA-Z0-9_-]{20,}",
            r"gsk_[a-zA-Z0-9_-]{20,}",
            r"Bearer\s+[a-zA-Z0-9._-]+",
        ]

        redacted_text = text

        for pattern in secret_patterns:
            redacted_text = re.sub(
                pattern,
                "[REDACTED]",
                redacted_text
            )

        return redacted_text

    def redact_pii(self, text: str) -> str:

        pii_patterns = [
            # Email
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",

            # Indian-style phone numbers
            r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
        ]

        redacted_text = text

        for pattern in pii_patterns:
            redacted_text = re.sub(
                pattern,
                "[PII REDACTED]",
                redacted_text
            )

        return redacted_text

    def is_casual_query(self, prompt: str) -> bool:
        casual_queries = {
            "hello",
            "hi",
            "hey",
            "hello there",
            "hi there",
            "hey there",
            "good morning",
            "good afternoon",
            "good evening",
            "how are you",
            "how are you?",
            "thanks",
            "thank you",
            "thanks!",
            "thank you!",
            "bye",
            "goodbye",
        }

        normalized_prompt = prompt.lower().strip()

        return normalized_prompt in casual_queries 