from functools import lru_cache
from io import BytesIO, TextIOWrapper

from jieba.analyse import ChineseAnalyzer
from whoosh.fields import TEXT, SchemaClass
from whoosh.filedb.filestore import RamStorage
from whoosh.index import FileIndex
from whoosh.qparser import QueryParser

storage = RamStorage()

analyzer = ChineseAnalyzer()


class ArticleSchema(SchemaClass):
    content = TEXT(stored=True, analyzer=analyzer)


schema = ArticleSchema()

_DEF_INDEX_NAME = "MAIN"


# use our own funtions instead of whoosh.index.create_in
# avoiding local storage
def _create_in(schema, indexname=None):
    if not indexname:
        indexname = _DEF_INDEX_NAME

    return FileIndex.create(storage, schema, indexname)


# def _open_dir(indexname=None, schema=None):

#     if not indexname:
#         indexname = _DEF_INDEX_NAME

#     return FileIndex(storage, schema=schema, indexname=indexname)


def build_index(book_id: str, content: bytes) -> FileIndex:
    try:
        ix = _create_in(schema, indexname=f"novel_index_{book_id}")
        writer = ix.writer()

        f = TextIOWrapper(BytesIO(content), encoding="utf-8")

        for line in f:
            writer.add_document(content=line.strip())

        writer.commit()

        return ix

    except Exception as e:
        print(e)
        return None


@lru_cache()
def query_by_prompt(ix: FileIndex, prompt: str) -> list:
    results = []

    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(prompt)
        _results = searcher.search(query)
        if len(_results) == 0:
            results.append("No results found.")
        else:
            for result in _results:
                results.append(result["content"])

    return results
