import rich
import typer

# from whoosh.index import create_in
from jieba.analyse import ChineseAnalyzer
from whoosh.fields import TEXT, SchemaClass
from whoosh.filedb.filestore import RamStorage
from whoosh.index import FileIndex

app = typer.Typer()

analyzer = ChineseAnalyzer()


class ArticleSchema(SchemaClass):
    content = TEXT(stored=True, analyzer=analyzer)


schema = ArticleSchema()

storage = RamStorage()

_DEF_INDEX_NAME = "MAIN"


def _create_in(schema, indexname=None):
    if not indexname:
        indexname = _DEF_INDEX_NAME

    return FileIndex.create(storage, schema, indexname)


def _open_dir(indexname=None, schema=None):
    if not indexname:
        indexname = _DEF_INDEX_NAME

    return FileIndex(storage, schema=schema, indexname=indexname)


@app.command()
def buildindex():
    ix = _create_in(schema, indexname="novel_index")
    writer = ix.writer()

    with open("novels/test.txt", "r", encoding="utf-8") as f:
        for line in f:
            writer.add_document(content=line.strip())

    writer.commit()


@app.command()
def search(prompt: str):
    from whoosh.qparser import QueryParser

    ix = _open_dir(indexname="novel_index")
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(prompt)
        results = searcher.search(query)
        if len(results) == 0:
            rich.print("No results found.")
        else:
            rich.print(results[0]["content"])


@app.command()
def interactive():
    buildindex()

    # load model
    from whoosh.qparser import QueryParser

    ix = _open_dir(indexname="novel_index")
    with ix.searcher() as searcher:
        while True:
            prompt = input(">>> ")

            if prompt == "exit":
                break

            query = QueryParser("content", ix.schema).parse(prompt)
            results = searcher.search(query)
            if len(results) == 0:
                rich.print("No results found.")
            else:
                rich.print(results[0]["content"])


if __name__ == "__main__":
    app()
