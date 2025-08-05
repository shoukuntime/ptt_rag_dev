import requests
from bs4 import BeautifulSoup


def ptt_scrape(board: str) -> list:
    board_url = 'https://www.ptt.cc/bbs/' + board + '/index.html'  # 首先建立看板網址
    board_html = get_html(board_url)  # 由看板網址取得 html
    article_urls = get_urls_from_board_html(board_html)  # 由看板 html 取得文章網址
    article_datas = []
    for article_url in article_urls:
        article_html = get_html(article_url)  # 由文章網址取得 html
        article_data = get_data_from_article_html(article_html)  # 由文章 html 取得文章資訊
        article_data.update({'board': board})  # 加入版面名稱資訊
        article_datas.append(article_data)  # 將文章資訊蒐集起來
    return article_datas  # 回傳文章資訊列表


def get_html(url: str) -> str:
    ...


def get_urls_from_board_html(html: str) -> list:
    ...


def get_data_from_article_html(html: str) -> dict:
    ...


if __name__ == "__main__":
    article_datas = ptt_scrape("Gossiping")
    for article_data in article_datas:
        print(article_data)
