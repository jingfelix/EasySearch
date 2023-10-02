from whoosh.filedb.filestore import Storage
from whoosh.filedb.structfile import StructFile
from server.app import db
from server.models import DBIndex

from io import BytesIO

class DBFile(StructFile):
    '''
    '''
    def __init__(self, name=None, onclose=None):
        self.is_closed = False
        self.is_real = False
        
        index = DBIndex.query.filter_by(name=name).first()
        if not index:
            raise ValueError("No such file")
        self.DBIndex = index[0]
        

    @property
    def file(self):
        # 从数据库中读取bytes转换为文件，返回文件对象
        # 注意，在修改时，需要对数据库进行修改
        return BytesIO(bytes(self.DBIndex.bytes))

    def write(self, *args, **kwargs):
        # 将bytes写入数据库
        self.DBIndex.bytes = self.file.read()
        db.session.commit()


class DBStorage(Storage):

    def __init__(self) -> None:
        # 为从数据库中读出的每个 DBIndex.name 创建一个 DBFile 对象
        index_list = DBIndex.query.all()
        self.files = {index.name: DBFile(index.name) for index in index_list}

    def open_file(self, name):
        if name not in self.files:
            raise ValueError("No such file")
        return self.files[name]

    def create_file(self, name, fileobj=None):
        if name in self.files:
            raise ValueError("File already exists")
        # 在数据库中创建一个新的 DBIndex
        db_index = DBIndex(name=name, bytes=fileobj.read())
        db.session.add(db_index)
        db.session.commit()

        # 更新 self.files
        self.files[name] = DBFile(name)

    def update_file(self, name, fileobj):
        # 将文件对象写入数据库
        self.files[name].write(fileobj)

def copy_storage_to_db(sourcestore, deststore):
    '''
    Note that destdb should be DBStorage
    '''
    for name in sourcestore.list():
        deststore.create_file(name)
        deststore.open_file(name).write(sourcestore.open_file(name).read())
