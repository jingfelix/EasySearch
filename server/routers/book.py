import logging

from functools import lru_cache
from flask import blueprints, jsonify, request, session

from server.models import BookFactory, Books, Book, QueryCache
from server.utils.auth import token_required
from server.utils.search import query_by_line_id, query_by_prompt, get_last_sentence

book_list = Books()

query_cache = QueryCache()

bp = blueprints.Blueprint("book", __name__, url_prefix="/book")


def make_response(code, msg, data=None):
    if data is None:
        data = {}
    return jsonify({"code": code, "msg": msg, "data": data})


@bp.route("", methods=["GET"])
def list_books():
    return make_response(0, "success", book_list.list_books())


@bp.route("", methods=["POST"])
@token_required
def upload_book():
    file = request.files.get("book")
    if not file:
        return make_response(1, "book is empty")

    name = file.filename.split(".")[0]

    try:
        aBook = BookFactory.create_book(name, file.read(), user_id = session["_id"])
        return make_response(0, "success", {"book_id": aBook.book_id})
    except ValueError as e:
        return make_response(1, str(e))


@bp.route("/<book_id>", methods=["GET"])
@token_required
def get_book_by_id(book_id):
    prompt = request.args.get("prompt", "")
    if not prompt:
        return make_response(1, "prompt is empty")

    aBook = book_list.get_book_by_id(book_id)
    if not aBook:
        return make_response(1, "book not found")

    ix = aBook.ix
    results = query_by_prompt(ix, prompt)  # 请确保已导入 query_by_prompt

    return make_response(0, "success", {"results": results})


@bp.route("/<book_id>/", methods=["DEL"])
@token_required
def delete_book_by_id(book_id):
    aBook = book_list.get_book_by_id(book_id)
    if not aBook:
        return make_response(1, "book not found")

    if book_list.del_book_by_id(book_id):
        return make_response(0, "success")
    else:
        return make_response(1, "failed to delete book")


@bp.route("/v1/<book_id>", methods=["GET"])
@token_required
def get_book_by_id_v1(book_id):
    prompt = request.args.get("prompt", "")

    if len(prompt) > 100:
        prompt = prompt[-100:]

    lastSentence = get_last_sentence(prompt)

    optional_num = request.args.get("number", 5)
    if optional_num > 10:
        optional_num = 10

    if not lastSentence:
        return make_response(1, "not found valid last prompt")

    aBook = book_list.get_book_by_id(book_id)
    if not aBook:
        return make_response(1, "book not found")

    ix = aBook.ix
    results = query_by_prompt(ix, lastSentence, optional_num)
    if len(results) == 0:
        results.append({"id": -1, "content": "No results found."})

    last_query: int = query_cache.get(user_id = session["_id"], book_id=book_id)
    if last_query != -1:
        # 排序依据：与上次查询的向后距离
        results.sort(key=lambda x: x["id"] - last_query)

    query_cache.set(user_id = session["_id"], book_id=book_id, result=results[0]["id"])

    # 判断是否是结尾段落的精准匹配
    bestComplete = results[0]
    if bestComplete["content"].endswith(lastSentence.strip()):
        line = int(bestComplete["id"])
        results = [{"id": line + 1, "content": query_by_line_id(ix, line + 1)}]
        return make_response(0, "success", {"results": results, "type": "next-line"})

    return make_response(0, "success", {"results": results, "type": "fuzzy"})


@bp.route("/<book_id>/<line_id>", methods=["GET"])
@token_required
def get_line_by_id(book_id, line_id):
    aBook = book_list.get_book_by_id(book_id)
    if not aBook:
        return make_response(1, "book not found")

    ix = aBook.ix
    try:
        line = query_by_line_id(ix, int(line_id))  # 请确保已导入 query_by_line_id
        result = {"id": line_id, "content": line}
        return make_response(0, "success", {"results": [result]})
    except ValueError:
        return make_response(1, "invalid line_id")


# 工具函数，用于检查书籍与用户是否匹配
@lru_cache()
def check_book_user(book_id, user_id)-> (bool, Book):
    aBook = book_list.get_book_by_id(book_id)
    if not aBook:
        return False
    return aBook.user_id == user_id, aBook
