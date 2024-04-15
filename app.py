from flask import Flask, render_template, request, jsonify, redirect, url_for
from crawling import crawl_news, create_dataframe
from txt_converter import csv_to_txt
from trending import nate_crawler, list_print
from summary import summarize_files
from divide import split_news_from_file
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    keywords = nate_crawler()
    result = list_print(keywords)
    if request.method == 'POST':
        search = request.form['search']
        page = int(request.form['page'])
        page2 = int(request.form['page2'])
        news_titles, final_urls, news_contents, news_dates = crawl_news(
            search, page, page2)
        csv_filename = create_dataframe(
            news_titles, final_urls, news_contents, news_dates, search)
        txt_content = csv_to_txt(csv_filename)
        txt_filename = f"{csv_filename.split('.')[0]}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as txt_file:
            txt_file.write(txt_content)

        # divide.py의 기능 호출
        split_news_from_file(txt_filename)

        # txt 파일 삭제
        os.remove(txt_filename)

        return redirect(url_for('summaries', search=search))  # 요약 페이지로 리다이렉트
    return render_template('index.html', keywords=result)


@app.route('/trending')
def trending():
    keywords = nate_crawler()
    result = list_print(keywords)
    return render_template('trending.html', keywords=result)


@app.route('/summaries')
def summaries():
    search = request.args.get('search')
    folder_path = 'C:\python_workspace'
    summaries = summarize_files(folder_path)

    # 요약 후에 txt 파일 삭제
    for summary in summaries:
        txt_filename = summary['file_path']
        os.remove(txt_filename)

    return render_template('summaries.html', summaries=summaries, search=search)


@app.route('/back_to_main')
def back_to_main():
    return redirect(url_for('index'))  # 메인 페이지로 리다이렉트


if __name__ == "__main__":
    app.run(debug=True)
