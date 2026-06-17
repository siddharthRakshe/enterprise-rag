from app.database.connection import engine
from app.database.models import User


def test_database():

    try:
        with engine.connect() as connection:
            print("✅ Database connected successfully!")
            print("✅ Users table found!")

    except Exception as e:
        print("❌ Database connection failed!")
        print(e)


if __name__ == "__main__":
    test_database()