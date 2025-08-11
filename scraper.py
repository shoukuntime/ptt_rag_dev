import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ptt_rag_dev.settings')
django.setup()

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
from article.models import Article


def get_html(url: str) -> str:
    session = requests.Session()
    payload = {
        "from": url,
        "yes": "yes"
    }
    session.post("https://www.ptt.cc/ask/over18", data=payload)
    response = session.get(url)
    return response.text


def get_urls_from_board_html(html: str) -> list:
    html_soup = BeautifulSoup(html, 'html.parser')
    r_ent_all = html_soup.find_all('div', class_='r-ent')
    urls = []
    for r_ent in r_ent_all:
        # 若無r_ent.find('a')['href']代表文章已刪除
        if r_ent.find('a'):
            if r_ent.find('a')['href']:
                urls.append('https://www.ptt.cc' + r_ent.find('a')['href'])
    return urls


def get_data_from_article_html(html: str) -> dict:
    html_soup = BeautifulSoup(html, 'html.parser')
    article_soup = html_soup.find('div', class_='bbs-screen bbs-content')
    title = article_soup.find_all('span', class_='article-meta-value')[2].text
    author = article_soup.find_all('span', class_='article-meta-value')[0].text.strip(')').split(' (')[0]
    time_str = article_soup.find_all('span', class_='article-meta-value')[3].text
    dt = datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
    dt = dt.replace(tzinfo=ZoneInfo("Asia/Taipei"))
    post_time = dt.strftime("%Y-%m-%d %H:%M:%S")

    result = []
    for element in article_soup.children:
        if element.name not in ["div", "span"]:
            text = element.get_text(strip=True) if element.name == "a" else str(element).strip()
            if text:
                result.append(text)
    content = "\n".join(result).strip('-')

    data = {
        'title': title,
        'author': author,
        'post_time': post_time,
        'content': content,
    }
    return data


def ptt_scrape(board: str) -> list:
    board_url = 'https://www.ptt.cc/bbs/' + board + '/index.html'  # 首先建立看板網址
    board_html = get_html(board_url)  # 由看板網址取得 html
    article_urls = get_urls_from_board_html(board_html)  # 由看板 html 取得文章網址
    article_id_list=[]
    for article_url in article_urls:
        article_html = get_html(article_url)  # 由文章網址取得 html
        article_data = get_data_from_article_html(article_html)  # 由文章 html 取得文章資訊
        article = Article.objects.create(
            board=board,
            title=article_data["title"],
            author=article_data["author"],
            url=article_url,
            content=article_data["content"],
            post_time=article_data["post_time"]
        )
        article_id_list.append(article.id)
    return article_id_list


if __name__ == "__main__":
    ptt_scrape('Gossiping')
    print('完成所有寫入!')
