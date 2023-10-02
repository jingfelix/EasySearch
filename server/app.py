import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret key"
app.config["LOG_FILENAME"] = "server.log"
app.config["LOG_LEVEL"] = logging.INFO
# 创建日志处理程序并添加到日志记录器中
log_handler = logging.FileHandler(app.config['LOG_FILENAME'])
log_handler.setLevel(app.config['LOG_LEVEL'])
app.logger.addHandler(log_handler)

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
db = SQLAlchemy(app)

from server.utils.storage import DBStorage
db_store = DBStorage()

from whoosh.filedb.filestore import RamStorage
storage = RamStorage()

from server.routers.book import bp as book_bp

app.register_blueprint(book_bp)
