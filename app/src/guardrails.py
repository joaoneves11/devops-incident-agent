
import re

# Block patterns that should not appear in agent output
BLOCKED_PATTERNS = [
    r"\b(rm\s+-rf\s+/|DROP\s+TABLE|TRUNCATE)\b",
    r"(\bpassword\s*=\s*[\"'][^\"']+[\"'])",
]


def validate_output(text: str) -> tuple[bool, list[str]]:
   
    violations = []
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(f"Blocked pattern detected: {pattern}")
    return (len(violations) == 0, violations)


def apply_guardrails(text: str) -> str:
   
    valid, violations = validate_output(text)
    if valid:
        return text
    return (
     "Resposta bloqueada por proteções de segurança."
     "Por favor, reformule ou evite comandos destrutivos ou sensíveis."
    )
