import os
# Define your JWT secret and algorithm
SECRET_KEY = os.getenv("SECRET_KEY", "MY SECRET KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")