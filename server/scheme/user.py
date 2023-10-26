from server.app import db
from server.scheme.base import BaseModel
from sqlalchemy import Column, String, Integer


class User(BaseModel):
    """用户与Token信息"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False, unique=True, comment='用户名')
    token = Column(String(80), nullable=False, unique=True, comment='Token')

    def __init__(self, name, token):
        self.name = name
        self.token = token

    def __repr__(self):
        result = {
            'name': self.name,
            'token': self.token
        }
        return str(result)