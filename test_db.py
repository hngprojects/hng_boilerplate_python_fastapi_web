from sqlalchemy import create_engine

def test_db_connection():
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_USER = "username"
    DB_PASSWORD = "password"
    DB_NAME = "test"
    DB_TYPE = "postgresql"

    DATABASE_URL = f"{DB_TYPE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    try:
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        print("Connection successful")
        connection.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_db_connection()
