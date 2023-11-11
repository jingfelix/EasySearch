import click
import time

import logging

from server.app import app, db, Encryptor
from server.scheme.user import User


@app.cli.command()
def admin():
    user = User(name="admin", token="")
    db.session.add(user)
    db.session.commit()

    token = Encryptor.encrypt(f"{user.id}:{time.time()}".encode("utf-8")).decode(
        "utf-8"
    )
    user.token = token
    click.echo(f"Admin: {user.id} {token}")
    logging.info(f"Admin: {user.id} {token}")

    db.session.add(user)
    db.session.commit()
    click.echo("Done.")


@app.cli.command()
def createdb():
    with app.app_context():
        db.create_all()
