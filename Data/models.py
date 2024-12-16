from sqlalchemy import Column, Integer, String, Sequence
from .database import base

class Task(base):
    __tablename__ = 'task'
    id = Column(Integer, Sequence("user_id"), primary_key=True)
    title = Column(String)
    description = Column(String)
    status = Column(String)