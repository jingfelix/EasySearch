from io import BytesIO, TextIOWrapper

from jieba.analyse import ChineseAnalyzer
from whoosh.fields import TEXT, SchemaClass
from whoosh.filedb.filestore import RamStorage
from whoosh.index import FileIndex

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


def buildindex(book_id: int, content: bytes) -> FileIndex:
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