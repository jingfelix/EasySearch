import json

from flask import blueprints, jsonify, request

from server.models import BookFactory, Books
from server.utils.search import query_by_line_id, query_by_prompt, get_last_sentence

book_list = Books()

bp = blueprints.Blueprint("book", __name__, url_prefix="/book")


def make_response(code, msg, data=None):
    if data is None:
        data = {}
    return jsonify({"code": code, "msg": msg, "data": data})


@bp.route("", methods=["GET"])
def list_books():
    return make_response(0, "success", book_list.list_books())


@bp.route("", methods=["POST"])
def upload_book():
    file = request.files.get("book")
    if not file:
        return make_response(1, "book is empty")

    name = file.filename.split(".")[0]

    try:
        aBook = BookFactory.create_book(name, file.read())
        return make_response(0, "success", {"book_id": aBook.book_id})
    except ValueError as e:
        return make_response(1, str(e))


@bp.route("/<book_id>", methods=["GET"])
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


@bp.route("/v1/<book_id>", methods=["GET"])
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

    # 判断是否是结尾段落的精准匹配
    bestComplete = results[0]
    if bestComplete["content"].endswith(lastSentence.strip()):
        line = int(bestComplete["id"])
        results = [{"id": line + 1, "content": query_by_line_id(ix, line + 1)}]
        return make_response(0, "success", {"results": results, "type": "next-line"})

    return make_response(0, "success", {"results": results, "type": "fuzzy"})


@bp.route("/<book_id>/<line_id>", methods=["GET"])
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
