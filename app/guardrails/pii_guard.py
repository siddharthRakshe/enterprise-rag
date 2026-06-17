import re


def check_pii_request(question):
    """
    Detect requests asking for sensitive personal information.
    Returns True if the request is safe.
    """

    sensitive_keywords = [
        "email",
        "email address",
        "phone number",
        "mobile number",
        "contact number",
        "aadhaar",
        "aadhar",
        "pan number",
        "passport",
        "credit card",
        "bank account",
        "salary",
        "employee details",
        "personal information",
        "social security number",
        "ssn"
    ]

    question = question.lower()

    for keyword in sensitive_keywords:
        if keyword in question:
            print(f"🔒 PII Request Detected: {keyword}")
            return False

    return True