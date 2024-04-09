import requests
from bs4 import BeautifulSoup
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_wordcloud_from_url(url, top_n=30):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    ranking_boxes = soup.find_all("div", "rankingnews_box")
    ranking_news_titles = []

    for ranking_box in ranking_boxes:
        article_list = ranking_box.find("ul", "rankingnews_list").find_all("li")
        for arti in article_list:
            content = arti.find("div", "list_content")
            if content:
                ranking_news_titles.append(content.find("a").text.strip())

    # 각 기사의 제목을 공백을 기준으로 단어로 분리하여 리스트에 저장
    words_list = []
    for title in ranking_news_titles:
        # 단어로 분리
        words = title.split()
        words_list.extend(words)

    # 각 단어의 등장 횟수 계산
    word_counts = Counter(words_list)

    # 워드 클라우드 생성
    wordCloud = WordCloud(
        font_path="malgun",  # 폰트 지정
        width=800,  # 워드 클라우드의 너비 지정
        height=600,  # 워드클라우드의 높이 지정
        max_font_size=100,  # 가장 빈도수가 높은 단어의 폰트 사이즈 지정
        background_color='white'  # 배경색 지정
    ).generate_from_frequencies(word_counts)  # 워드 클라우드 빈도수 지정

    # 워드 클라우드 출력
    pig = plt.figure()
    plt.imshow(wordCloud)
    plt.axis('off')
    plt.show()
    return pig

generate_wordcloud_from_url('https://news.naver.com/main/ranking/popularDay.naver')