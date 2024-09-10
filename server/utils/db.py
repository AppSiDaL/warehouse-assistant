from sqlalchemy import create_engine,StaticPool
from sqlalchemy.orm import sessionmaker,declarative_base
from .config import DB_URL,ENV

try:
    if ENV=="testing":
        engine = create_engine(
            DB_URL,
            connect_args={
                "check_same_thread": False,
            },
            poolclass=StaticPool,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    engine = create_engine(DB_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

except Exception as e:
    print("Error: ", e)

Base = declarative_base()