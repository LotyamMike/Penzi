from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# Replace with your actual database URL
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:Lotty%40488@localhost/Penzi_db" 

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close() 