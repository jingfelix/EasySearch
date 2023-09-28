from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret key"

from server.routers.book import bp as book_bp

app.register_blueprint(book_bp)
