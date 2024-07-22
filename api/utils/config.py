import os
# Define your JWT secret and algorithm
SECRET_KEY = os.getenv("SECRET_KEY", "MY SECRET KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
    
