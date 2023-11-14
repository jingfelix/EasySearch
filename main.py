import logging

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


def make_admin():
    with app.app_context():
        _user = User.query.filter_by(name="admin").first()
        if _user:
            logging.info("Admin already exists.")
            return

        user = User(name="admin", token="")
        db.session.add(user)
        db.session.commit()

        token = Encryptor.encrypt(f"{user.id}:{time.time()}".encode("utf-8")).decode(
            "utf-8"
        )
        user.token = token
        logging.info(f"Admin: {user.id} {token}")
        logging.info(f"Admin: {user.id} {token}")

        db.session.add(user)
        db.session.commit()
        logging.info("Done.")


if __name__ != "__main__":
    guni_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = guni_logger.handlers
    app.logger.setLevel(guni_logger.level)

    make_admin()
    show_admin()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
