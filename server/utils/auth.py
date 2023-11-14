import time
from functools import wraps
from typing import Tuple

from flask import jsonify, request, session

from server.app import app, Encryptor
from server.scheme.user import User

def encrypt_token(id: int) -> str:
    return Encryptor.encrypt(f"{id}:{time.time()}".encode("utf-8")).decode("utf-8")


def decrypt_token(token: str) -> Tuple[int, float]:
    try:
        data = Encryptor.decrypt(token.encode("utf-8")).decode("utf-8")
        id, timestamp = data.split(":")
        return int(id), float(timestamp)
    except:
        return None, None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token is None:
            return jsonify({"message": "Token is missing!"}), 403
        token = token.split(" ")[-1]
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            id, timestamp = decrypt_token(token)
            if not id or not timestamp:
                return jsonify({"message": "Token is invalid!"}), 403
            # if time.time() - timestamp > app.config["TOKEN_EXPIRATION"]:
            #     return jsonify({"message": "Token is expired!"}), 403

            # 检查是否有对应的用户
            user = User.query.get(id)
            if not user:
                return jsonify({"message": "Token is invalid!"}), 403

            session["_id"] = id

        except:
            return jsonify({"message": "Token is invalid!"}), 403
        return f(*args, **kwargs)

    return decorated
