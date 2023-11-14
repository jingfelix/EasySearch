import os
from flask import Flask
import logging

from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

from cryptography.fernet import Fernet

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret key"
app.config["TOKEN_EXPIRED"] = 1000 * 3600 * 24 * 365
app.config["LOG_FILENAME"] = "server.log"
app.config["LOG_LEVEL"] = logging.INFO
log_handler = logging.FileHandler(app.config['LOG_FILENAME'])
log_handler.setLevel(app.config['LOG_LEVEL'])
app.logger.addHandler(log_handler)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy()
db.init_app(app)

cache = Cache(app,config={'CACHE_TYPE': 'SimpleCache'})

if not os.path.exists(os.path.join(app.instance_path, ".secret")):
    with open(os.path.join(app.instance_path, ".secret"), "wb") as f:
        secret = Fernet.generate_key()
        f.write(secret)

with open(os.path.join(app.instance_path, ".secret"), "rb") as f:
    secret = f.read()

Encryptor = Fernet(secret)

from server.routers.book import bp as book_bp, book_list

app.register_blueprint(book_bp)

with app.app_context():
    db.create_all()

book_list.init()