from flask import Flask
import logging

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret key"

# 创建日志处理程序并添加到日志记录器中
log_handler = logging.FileHandler(app.config['LOG_FILENAME'])
log_handler.setLevel(app.config['LOG_LEVEL'])
app.logger.addHandler(log_handler)

from server.routers.book import bp as book_bp

app.register_blueprint(book_bp)
