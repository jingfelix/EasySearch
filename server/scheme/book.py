from server.app import db
from server.scheme.base import BaseModel
from server.scheme.user import User
from sqlalchemy import Column, Integer, String, Boolean


class BookMeta(BaseModel):
    """书籍信息"""
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(32), nullable=False, unique=True, comment='UUID')
    title = Column(String(80), nullable=False, comment='书名')
    md5 = Column(String(32), nullable=True, comment='文件MD5')
    index_path = Column(String(80), nullable=True, comment='索引路径')

    user_id = Column(Integer, db.ForeignKey('user.id'), nullable=False, comment='用户ID')

    def __init__(self, uuid, title, md5=None, index_path=None, user_id=None):
        self.uuid = uuid
        self.title = title
        self.md5 = md5
        self.index_path = index_path
        self.user_id = user_id

    def __repr__(self):
        result = {
            'uuid': self.uuid,
            'title': self.title,
            'md5': self.md5,
            'index_path': self.index_path,
            'user_id': self.user_id
        }
        return str(result)
