import re


def check_output_safety(response):
    """
    Check whether the LLM response contains
    sensitive or unsafe information.
    Returns True if the response is safe.
    """

    dangerous_patterns = [
        r"password",
        r"secret key",
        r"api key",
        r"private key",
        r"token",
        r"\b\d{12}\b",              # Aadhaar-like numbers
        r"\b\d{16}\b",              # Credit card-like numbers
        r"\S+@\S+\.\S+"             # Email addresses
    ]

    response = response.lower()

    for pattern in dangerous_patterns:
        if re.search(pattern, response):
            print(
                f"🛑 Output Guard Blocked Pattern: {pattern}"
            )
            return False

    return True