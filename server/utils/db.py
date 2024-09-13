from sqlalchemy import create_engine, StaticPool, event
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DB_URL, ENV

def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')

try:
    if ENV == "testing":
        engine = create_engine(
            DB_URL,
            connect_args={
                "check_same_thread": False,
            },
            poolclass=StaticPool,
        )
        event.listen(engine, 'connect', _fk_pragma_on_connect)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    else:
        engine = create_engine(DB_URL, echo=True)
        event.listen(engine, 'connect', _fk_pragma_on_connect)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

except Exception as e:
    print("Error: ", e)

Base = declarative_base()