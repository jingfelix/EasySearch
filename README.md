# Easy Search

## 使用

提供了一个简单的 jupyter notebook 用于演示。依次执行前两个代码块来上传文本，在最后一个代码块中修改 `prompt` 的值来进行提问。

或使用 mvp.py 来进行简单的交互式对话（默认使用了novels/test.txt）
```bash
python3 mvp.py interactive
```

## API reference

- GET /book/
    - 返回所有书籍的book_id和filename

- POST /book/
    - 上传书籍，成功则返回book_id
    - 对书籍文件的要求：每行一个句子（匹配时按句子为单位返回）
    ```python
    import requests
    res = requests.post('http://localhost:5000/book/', files={'file': open('test.txt', 'rb')})
    book_id = res.json()['data']['book_id']
    ```

- POST /book/{book_id}?prompt=
    - 查询书籍中与prompt相似句子，返回一个列表
    ```python
    import requests
    res = requests.post('http://localhost:5000/book/b24a24a5-d166-458c-a794-d64733737c35?prompt=物理学从来没有')
    print(res.json()['data']['results'])
    ```

## TODOs

- 对文本的更多处理，如去除 prompt 中的标点
- 优化存储池，增加过期时间，搜索缓存
- 考虑将分词的过程换为异步的

- 选择补全句子/段落
- 如何查找相邻的段落/句子？
    - 多标签搜索
    - issue #4

- 找一下可用的前端
    - Novel/类Copilot