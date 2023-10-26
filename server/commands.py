import click
import time

from server.app import app, db, Encryptor
from server.scheme.user import User

@app.cli.command()
def admin():
    user = User(name='admin', token='')
    db.session.add(user)
    db.session.commit()

    token = Encryptor.encrypt(f"{user.id}:{time.time()}".encode("utf-8")).decode("utf-8")
    user.token = token
    click.echo(f'Admin: {user.id} {token}')

    db.session.add(user)
    db.session.commit()
    click.echo('Done.')

@app.cli.command()
def create_db():
    with app.app_context():
        db.create_all()