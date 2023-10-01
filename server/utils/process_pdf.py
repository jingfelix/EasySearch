import logging

import pdfplumber
from flask import current_app
import json

if current_app:
    logger = current_app.logger
else:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


def filter_chapter_min_length(chapters: list, min_length: int = 10):
    return [chapter for chapter in chapters if len(chapter["content"]) > min_length]


def check_chapter_sequence(chapters: list):
    for i in range(len(chapters) - 1):
        if int(chapters[i + 1]["title"]) - int(chapters[i]["title"]) != 1:
            logger.warning(f"章节号不连续：{chapters[i]}")
            return False
    logger.info('章节号连续检测通过')
    return True


def process_pdf(pdf_file):
    logger.info(f"Processing {pdf_file} ...")
    with pdfplumber.open(pdf_file) as pdf:
        chapters = []
        chapter = {"title": "", "content": ""}
        for page in pdf.pages:
            text = page.extract_text()
            for line in text.split('\n'):
                if not line:
                    continue
                if line.isdigit():
                    if chapter["title"]:  # 将上一章节添加到 chapters 列表中去（如果存在）
                        chapters.append(chapter)
                    chapter = {"title": line, "content": ""}  # 创建新章节
                else:
                    chapter["content"] += line + '\n'
        if chapter["title"]:  # 添加最后一章到 chapters 列表中去（如果存在）
            chapters.append(chapter)

    chapters = filter_chapter_min_length(chapters, 10)
    check_chapter_sequence(chapters)

    title = pdf_file.split('/')[-1].replace('.pdf', '')
    res = {"title": title, "chapter": chapters}

    json_file = pdf_file.replace('.pdf', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)
    logger.info(f"Saved {json_file}")


if __name__ == '__main__':
    logger.info('start main function')

