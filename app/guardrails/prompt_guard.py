def check_prompt_safety(question):
    """
    Detect possible prompt injection attempts.
    Returns True if the question is safe.
    """

    dangerous_patterns = [
        "ignore previous instructions",
        "ignore all instructions",
        "forget previous instructions",
        "forget all instructions",
        "disregard instructions",
        "override instructions",
        "bypass security",
        "developer mode",
        "system prompt",
        "act as",
        "you are now",
        "pretend to be",
        "jailbreak"
    ]

    question = question.lower()

    for pattern in dangerous_patterns:
        if pattern in question:
            print(f"🚨 Prompt Injection Detected: {pattern}")
            return False

    return True