import os
import pickle
from functools import lru_cache
from io import BytesIO, TextIOWrapper

import pdfplumber
from jieba.analyse import ChineseAnalyzer
from whoosh.fields import ID, TEXT, SchemaClass
from whoosh.filedb.filestore import RamStorage
from whoosh.index import FileIndex, open_dir,create_in
from whoosh.qparser import QueryParser

storage = RamStorage()

analyzer = ChineseAnalyzer()



class ArticleSchema(SchemaClass):
    content = TEXT(stored=True, analyzer=analyzer)
    line_id = ID(stored=True)


schema = ArticleSchema()

_DEF_INDEX_NAME = "MAIN"


# 文件夹用来保存持久化的索引对象
INDEX_DIR = "index_ix"
if not os.path.exists(INDEX_DIR):
    os.mkdir(INDEX_DIR)

# use our own funtions instead of whoosh.index.create_in
# avoiding local storage
def _create_in(schema, indexname=None):
    if not indexname:
        indexname = _DEF_INDEX_NAME

    return FileIndex.create(storage, schema, indexname)


def build_index(book_id: str, content: bytes) -> FileIndex:
    try:
        # 创建以书籍ID为前缀的文件夹
        index_folder_path = os.path.join(INDEX_DIR, f"novel_index_{book_id}")        # 尝试从持久化文件中加载索引
        if not os.path.exists(index_folder_path):
            os.mkdir(index_folder_path)
            ix = create_in(index_folder_path,schema, indexname=book_id)
            # 扫描并添加文本内容到索引
            writer = ix.writer()
            f = TextIOWrapper(BytesIO(content), encoding="utf-8")
            line_id = 0
            for line in f:
                writer.add_document(content=line.strip(), line_id=str(line_id))
                line_id += 1

            writer.commit()
        else:
            ix = open_dir(index_folder_path)
        return ix

    except Exception as e:
        print(e)
        return None

def load_index(book_id: str):
    index_folder_path = os.path.join(INDEX_DIR, f"novel_index_{book_id}")
    if not os.path.exists(index_folder_path):
        return None
    ix = open_dir(index_folder_path,indexname=book_id)
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


