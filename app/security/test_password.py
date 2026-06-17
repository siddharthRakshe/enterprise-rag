from app.security.password import (
    hash_password,
    verify_password
)


def test_password_security():

    password = "admin123"

    print("Original Password:")
    print(password)

    print("\nGenerating hash...")

    hashed = hash_password(password)

    print("\nGenerated Hash:")
    print(hashed)

    print("\nTesting correct password:")

    result = verify_password(
        "admin123",
        hashed
    )

    print("Result:", result)

    print("\nTesting wrong password:")

    result = verify_password(
        "wrongpassword",
        hashed
    )

    print("Result:", result)


if __name__ == "__main__":
    test_password_security()