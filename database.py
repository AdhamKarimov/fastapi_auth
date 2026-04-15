from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:123@localhost/fastapi_db')

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()   


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()