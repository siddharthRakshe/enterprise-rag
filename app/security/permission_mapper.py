def get_required_permission(question):
    """
    Convert user question into required permission.
    """

    question = question.lower()


    # Salary and finance
    if any(keyword in question for keyword in [
        "salary",
        "pay",
        "compensation",
        "financial",
        "finance",
        "money"
    ]):
        return "view_salary_data"


    # Employee records
    if any(keyword in question for keyword in [
        "employee record",
        "employee details",
        "employee information",
        "personal data"
    ]):
        return "view_employee_records"


    # Team reports
    if any(keyword in question for keyword in [
        "team report",
        "performance report"
    ]):
        return "view_team_reports"


    # Office timings
    if any(keyword in question for keyword in [
        "office timing",
        "office time",
        "working hours",
        "work timing"
    ]):
        return "view_office_timing"


    # HR policies
    if any(keyword in question for keyword in [
        "leave",
        "leaves",
        "holiday",
        "vacation",
        "work from home",
        "wfh",
        "insurance",
        "medical",
        "policy",
        "hr"
    ]):
        return "view_hr_policy"


    # Default: general company policies
    return "view_hr_policy"