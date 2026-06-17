from datetime import datetime
import os


LOG_FILE = "audit.log"


def log_event(user_role, question, action, details):
    """
    Store audit events in a log file.
    """

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    log_message = (
        f"[{timestamp}] "
        f"ROLE={user_role} | "
        f"QUESTION={question} | "
        f"ACTION={action} | "
        f"DETAILS={details}\n"
    )


    with open(LOG_FILE, "a") as file:
        file.write(log_message)


    print("📜 Audit Logged")