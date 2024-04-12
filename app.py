from flask import Flask, render_template, request, jsonify
from crawling import crawl_news, create_dataframe
from txt_converter import csv_to_txt
from trending import nate_crawler, list_print
from summary import summarize_files
from divide import split_news_from_file
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
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

        return jsonify({"message": f"Text file '{txt_filename}' has been created."}), 200
    return render_template('index.html')


@app.route('/trending')
def trending():
    keywords = nate_crawler()
    result = list_print(keywords)
    return render_template('trending.html', keywords=result)


@app.route('/summaries')
def summaries():
    folder_path = 'C:\python_workspace'
    summaries = summarize_files(folder_path)
    
    # 요약 후에 txt 파일 삭제
    for summary in summaries:
        txt_filename = summary['file_path']
        os.remove(txt_filename)

    return render_template('summaries.html', summaries=summaries)



if __name__ == "__main__":
    app.run(debug=True)
