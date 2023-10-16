from flask import Flask
import logging

from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret key"
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


from server.routers.book import bp as book_bp, book_list

app.register_blueprint(book_bp)

with app.app_context():
    db.create_all()

book_list.init()