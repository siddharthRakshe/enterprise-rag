# Role-Based Access Control (RBAC)

ROLE_PERMISSIONS = {

    "employee": [
        "view_hr_policy",
        "view_office_timing"
    ],

    "manager": [
        "view_hr_policy",
        "view_office_timing",
        "view_team_reports"
    ],

    "hr_admin": [
        "view_hr_policy",
        "view_office_timing",
        "view_employee_records"
    ],

    "finance": [
        "view_salary_data",
        "view_financial_reports"
    ],

    "admin": [
        "all_access"
    ]
}


def check_permission(user_role, required_permission):
    """
    Check whether a role can access a permission.
    """

    # Check if role exists
    if user_role not in ROLE_PERMISSIONS:
        print(f"❌ Unknown role: {user_role}")
        return False


    permissions = ROLE_PERMISSIONS[user_role]


    # Admin bypass
    if "all_access" in permissions:
        return True


    # Normal permission check
    if required_permission in permissions:
        return True


    print(
        f"🚫 Access denied. Role '{user_role}' does not have '{required_permission}' permission."
    )

    return False