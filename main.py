import logging

from flask import current_app

from server.app import app
from server.scheme.user import User
from server.commands import *

def show_admin():

    with app.app_context():
        admin = User.query.filter_by(name="admin").first()
        if admin is None:
            app.logger.info("Admin not found")
        else:
            app.logger.info(f"Admin: {admin.name} {admin.token}")


if __name__ != "__main__":
    guni_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = guni_logger.handlers
    app.logger.setLevel(guni_logger.level)

    show_admin()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
