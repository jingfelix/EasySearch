import os
from functools import lru_cache
from io import BytesIO, TextIOWrapper

from jieba.analyse import ChineseAnalyzer
from whoosh.fields import ID, TEXT, SchemaClass, Schema
from whoosh.filedb.filestore import RamStorage
from whoosh.index import FileIndex, open_dir, create_in
from whoosh.qparser import QueryParser

storage = RamStorage()

analyzer = ChineseAnalyzer()


class ArticleSchema(SchemaClass):
    content = TEXT(stored=True, analyzer=analyzer)
    line_id = ID(stored=True)


INDEX_DIR = "index_ix"


def get_index_dir(book_id: str) -> str:
    return os.path.join(INDEX_DIR, f"novel_index_{book_id}")


def create_or_open_index(book_id: str, schema_: Schema) -> FileIndex:
    index_folder_path = get_index_dir(book_id)
    if not os.path.exists(index_folder_path):
        os.makedirs(index_folder_path, exist_ok=True)
        return create_in(index_folder_path, schema_, indexname=book_id)
    else:
        return open_dir(index_folder_path, indexname=book_id)


def create_article_schema() -> Schema:
    analyzer_ = ChineseAnalyzer()
    return Schema(content=TEXT(stored=True, analyzer=analyzer_), line_id=ID(stored=True))


def build_index(book_id: str, content: bytes) -> FileIndex | None:
    try:
        schema_ = create_article_schema()
        ix = create_or_open_index(book_id, schema_)
        writer = ix.writer()
        f = TextIOWrapper(BytesIO(content), encoding="utf-8")
        line_id = 0
        for line in f:
            writer.add_document(content=line.strip(), line_id=str(line_id))
            line_id += 1
        writer.commit()
        return ix
    except Exception as e:
        print(e)
        return None


def load_index(book_id: str):
    index_folder_path = get_index_dir(book_id)
    if not os.path.exists(index_folder_path):
        return None
    ix = open_dir(index_folder_path, indexname=book_id)
    return ix


@lru_cache()
def query_by_prompt(ix: FileIndex, prompt: str) -> list:
    results = []
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(prompt)
        _results = searcher.search(query)
        if len(_results) == 0:
            results.append({"id": -1, "content": "No results found."})
        else:
            for result in _results:
                results.append({
                    "id": result["line_id"],
                    "content": result["content"]
                })

    return results


@lru_cache()
def query_by_line_id(ix: FileIndex, line_id: int) -> str:
    with ix.searcher() as searcher:
        results = [line for line in searcher.documents(line_id=str(line_id))]

    if len(results) != 0:
        return results[0]["content"]
    else:
        return "No results found."
