# #!/usr/bin/env python3
""" The database module
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from api.utils.settings import settings, BASE_DIR


DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_NAME = settings.DB_NAME
DB_TYPE = settings.DB_TYPE


def get_db_engine(test_mode: bool = False):
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    if DB_TYPE == "sqlite" or test_mode:
        BASE_PATH = f"sqlite:///{BASE_DIR}"
        DATABASE_URL = BASE_PATH + "/"
        
        if test_mode:
            DATABASE_URL = BASE_PATH + "test.db"
            
            return create_engine(
                DATABASE_URL, connect_args={"check_same_thread": False}
            )
    elif DB_TYPE == "postgresql":
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
    return create_engine(DATABASE_URL)
        
engine = get_db_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db_session = scoped_session(SessionLocal)

Base = declarative_base()

def create_database():
    return Base.metadata.create_all(bind=engine)

def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


#!/usr/bin/env python3
# """ The database module
# """
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from decouple import config
# from contextlib import contextmanager
# from api.v1.models.base import Base
# from api.v1.models.user import User, WaitlistUser
# from api.v1.models.org import Organization
# from api.v1.models.profile import Profile
# from api.v1.models.product import Product
# from api.v1.models.subscription import Subscription
# from api.v1.models.blog import Blog
# from api.v1.models.job import Job

# def get_db_engine():

#     DB_TYPE = config("DB_TYPE", "postgresql")
#     DB_NAME = config("DB_NAME", "hng_fast_api")
#     DB_USER = config("DB_USER", "")
#     DB_PASSWORD = config("DB_PASSWORD", "")
#     DB_HOST = config("DB_HOST", "localhost")
#     DB_PORT = config("DB_PORT", "5432")
#     MYSQL_DRIVER = config("MYSQL_DRIVER", "")
#     DATABASE_URL = ""

#     if DB_TYPE == "mysql":
#         DATABASE_URL = f'mysql+{MYSQL_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
#     elif DB_TYPE == "postgresql":
#         DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
#     else:
#         DATABASE_URL = "sqlite:///./database.db"

#     if DB_TYPE == "sqlite":
#         db_engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
#     else:
#         db_engine = create_engine(DATABASE_URL, pool_size=32, max_overflow=64)
    
#     return db_engine

# db_engine = get_db_engine()


# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


# def create_database():
#     return Base.metadata.create_all(bind=db_engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# create_database()
# db = next(get_db())
