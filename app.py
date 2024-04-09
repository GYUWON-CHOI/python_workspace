from flask import Flask, render_template, request, jsonify
from crawling import crawl_news, create_dataframe
from txt_converter import csv_to_txt

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search = request.form['search']
        page = int(request.form['page'])
        page2 = int(request.form['page2'])
        news_titles, final_urls, news_contents, news_dates = crawl_news(search, page, page2)
        csv_filename = create_dataframe(news_titles, final_urls, news_contents, news_dates, search)
        txt_content = csv_to_txt(csv_filename)
        txt_filename = f"{csv_filename.split('.')[0]}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as txt_file:
            txt_file.write(txt_content)
        return jsonify({"message": f"Text file '{txt_filename}' has been created."}), 200
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
