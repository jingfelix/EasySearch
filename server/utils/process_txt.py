import re

# 使用了 https://github.com/blmoistawinde/HarvestText 的分句函数
def cut_sentences(para, drop_empty_line=True, strip=True, deduplicate=False)->list[str]:
    '''cut_sentences

    :param para: 输入文本
    :param drop_empty_line: 是否丢弃空行
    :param strip: 是否对每一句话做一次strip
    :param deduplicate: 是否对连续标点去重，帮助对连续标点结尾的句子分句
    :return: sentences: list of str
    '''
    if deduplicate:
        para = re.sub(r"([。！？\!\?])\1+", r"\1", para)

    para = re.sub('([。！？\?!])([^”’)\]）】])', r"\1\n\2", para)  # 单字符断句符
    para = re.sub('(\.{3,})([^”’)\]）】….])', r"\1\n\2", para)  # 英文省略号
    para = re.sub('(\…+)([^”’)\]）】….])', r"\1\n\2", para)  # 中文省略号
    para = re.sub('([。！？\?!]|\.{3,}|\…+)([”’)\]）】])([^，。！？\?….])', r'\1\2\n\3', para)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    para = para.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    sentences = para.split("\n")
    if strip:
        sentences = [sent.strip() for sent in sentences]
    if drop_empty_line:
        sentences = [sent for sent in sentences if len(sent.strip()) > 0]
    return sentences

def cut_sentences_spacy(text: str)->list[str]:
    import spacy
    nlp = spacy.load("zh_core_web_sm")
    doc = nlp(text)

    return [sent.text for sent in doc.sents]

if __name__ == "__main__":
    with open("novels/test.txt", "r", encoding="utf-8") as f:
        with open("novels/test2.txt", "w", encoding="utf-8") as f2:
            text = f.read()
            for line in cut_sentences(text, deduplicate=True):
                f2.write(line + "\n")

        print("phase 1 done")

        with open("novels/test3.txt", "w", encoding="utf-8") as f2:
            f.seek(0)
            text = "".join([line.strip() for line in f.readlines()])
            for line in cut_sentences_spacy(text):
                if line.strip() != "":
                    f2.write(line + "\n")

        print("phase 2 done")