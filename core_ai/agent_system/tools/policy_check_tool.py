from typing import Dict

def policy_check(question: str) -> Dict[str, object]:
    """
    Simple policy gate for enterprise scenarios.
    Returns: {"allowed": bool, "reason": str}
    """
    q = question.lower()

    blocked_keywords = [
        "password",
        "otp",
        "secret",
        "secret key",
        "api key",
        "token",
        "private key",
        "credit card",
        "cvv",
    ]

    for kw in blocked_keywords:
        if kw in q:
            return {"allowed": False, "reason": f"Sensitive request detected: '{kw}'"}

    return {"allowed": True, "reason": "ok"}
