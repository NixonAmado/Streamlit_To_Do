from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()

def init_db():
    engine = create_engine('sqlite:///gestorTareas.db')
    base.metadata.create_all(engine)
    return engine

