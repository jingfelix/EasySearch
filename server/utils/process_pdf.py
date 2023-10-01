import logging
import spacy
import pdfplumber
from flask import current_app


def setup_logger():
    """
    设置日志记录器，如果在 Flask 应用上下文中运行，则使用当前应用程序的日志记录器，否则创建一个新的日志记录器。

    Returns:
        logger: 配置好的日志记录器对象
    """
    if current_app:
        logger = current_app.logger
    else:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
    return logger


# 当下面每一行少于最小字的时候，就必须和上一行合并
def format_limit_length(sents: list, minimum_length: int = 20):
    """
    将文本句子列表按照最小长度要求进行合并。

    Args:
        sents (list): 文本句子列表
        minimum_length (int): 最小长度要求

    Returns:
        list: 合并后的句子列表
    """
    res = []
    temp = ''
    for sent in sents:
        if len(sent) > minimum_length:
            res.append(temp)
            temp = sent
        else:
            temp += sent
    return res

def process_pdf_to_sentence(pdf_file):
    """
   从 PDF 文件中提取文本，进行句子分割，并保存到文本文件中。

   Args:
       pdf_file (str): 输入的 PDF 文件路径
   """
    logger = setup_logger()
    logger.info(f"Processing {pdf_file} ...")

    output_file = pdf_file.replace('.pdf', '.txt')
    paragraphs = []

    with pdfplumber.open(pdf_file) as pdf:
        _all_text = ''.join(page.extract_text().replace('\n', '') for page in pdf.pages)

    # python -m spacy download zh_core_web_sm  下载中文模型
    nlp = spacy.load("zh_core_web_sm")
    doc = nlp(_all_text)

    paragraphs = [sent.text for sent in doc.sents]

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(paragraphs))

    logger.info(f"Saved {output_file}")


def format_text_limit_length(text_path):
    """
   格式化给定文本文件中的文本，按照最小长度要求进行句子合并。

   Args:
       text_path (str): 输入的文本文件路径
    """
    logger = setup_logger()
    logger.info(f"Formatting {text_path} ...")

    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()

    paragraphs = text.split('\n')
    paragraphs = format_limit_length(paragraphs)

    with open(text_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(paragraphs))


if __name__ == '__main__':
    logger = setup_logger()
    logger.info('Start main function')
    process_pdf_to_sentence("../../novels/维罗妮卡决定去死.pdf")
    format_text_limit_length("../../novels/维罗妮卡决定去死.txt")
