from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from crawling import crawl_news, create_dataframe
from txt_converter import csv_to_txt
from trending import nate_crawler, list_print
from summary import summarize_files
from divide import split_news_from_file
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from datetime import datetime
from weather import get_weather_data
import os
import requests

app = Flask(__name__)
api_key = ''

# MySQL 설정
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'user_info'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = 'QWER'

mysql = MySQL(app)


def is_logged_in():
    return 'logged_in' in session


@app.route('/', methods=['GET', 'POST'])
def index():
    if not is_logged_in():  # 로그인하지 않은 경우 로그인 페이지로 리다이렉트
        return redirect(url_for('login'))
    
    # 초기화
    weather_data = None
    error_message = None

    # 서울 날씨 정보 가져오기
    city = "Seoul"
    weather_data = get_weather_data(city, api_key)
    if weather_data['cod'] != 200:
        error_message = "도시를 찾을 수 없습니다."
        weather_data = None
    else:
        city_name = weather_data['name']
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        weather = weather_data['weather'][0]['description']
        feels_like = weather_data['main']['feels_like']
        temp_min = weather_data['main']['temp_min']
        temp_max = weather_data['main']['temp_max']
        icon = weather_data['weather'][0]['icon']

    # 최대 3개의 게시물 가져오기
    posts = get_posts()[:4]

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

    return render_template('index.html', posts=posts, keywords=result, is_logged_in=is_logged_in, city_name=city_name, current_time=current_time,
                           weather=weather, feels_like=feels_like, temp_min=temp_min,
                           temp_max=temp_max, icon=icon, error_message=error_message)


# MySQL에서 게시물 데이터 가져오기
def get_posts():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts")
    posts = cur.fetchall()
    cur.close()
    return posts


@app.route('/trending')
def trending():
    keywords = nate_crawler()
    result = list_print(keywords)
    return render_template('trending.html', keywords=result)


@app.route('/summaries')
def summaries():
    search = request.args.get('search')
    folder_path = 'C:\python_workspace-main'  # 경로 수정
    summaries = summarize_files(folder_path)

    # 요약 후에 txt 파일 삭제
    for summary in summaries:
        txt_filename = summary['file_path']
        os.remove(txt_filename)

    return render_template('summaries.html', summaries=summaries, search=search, is_logged_in=is_logged_in)


@app.route('/back_to_main')
def back_to_main():
    return redirect(url_for('index'))  # 메인 페이지로 리다이렉트


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 폼 데이터 가져오기
        email = request.form['email']
        password_candidate = request.form['password']

        # MySQL에서 사용자 가져오기
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            # 비밀번호 검증
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['email'] = email
                return redirect(url_for('index'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Email not found'
            return render_template('login.html', error=error)

    return render_template('login.html', is_logged_in=is_logged_in)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 폼 데이터 가져오기
        name = request.form['name']
        email = request.form['email']
        password = sha256_crypt.encrypt(
            str(request.form['password']))  # 비밀번호 암호화

        # MySQL에 사용자 추가
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users(name, email, password) VALUES(%s, %s, %s)", (name, email, password))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))  # 로그아웃 후 로그인 페이지로 리다이렉트


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/board', methods=['GET', 'POST'])
def board():
    page = request.args.get('page', 1, type=int)
    per_page = 5

    if request.method == 'POST':
        if not is_logged_in():
            return redirect(url_for('login'))

        title = request.form['title']
        content = request.form['content']
        user_email = session['email']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO posts (title, content, user_email) VALUES (%s, %s, %s)", (title, content, user_email))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('board'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts")
    posts = cur.fetchall()
    cur.close()

    total_posts = len(posts)
    total_pages = (total_posts + per_page - 1) // per_page

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_posts)
    posts_to_display = posts[start_idx:end_idx]

    return render_template('board.html', posts=posts_to_display, is_logged_in=is_logged_in, total_pages=total_pages, current_page=page)



@app.route('/board/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts WHERE id = %s", [post_id])
    post = cur.fetchone()

    comments = get_comments(post_id)
    cur.close()

    return render_template('post.html', post=post, comments=comments, is_logged_in=is_logged_in)
# 댓글 저장
@app.route('/board/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    content = request.form['content']
    user_email = session['email']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO comments (post_id, user_email, content) VALUES (%s, %s, %s)", (post_id, user_email, content))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('view_post', post_id=post_id))

# 댓글 가져오기
def get_comments(post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM comments WHERE post_id = %s ORDER BY created_at DESC", [post_id])
    comments = cur.fetchall()
    cur.close()
    return comments

@app.route('/board/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts WHERE id = %s", [post_id])
    post = cur.fetchone()
    cur.close()

    if post['user_email'] != session['email']:
        return redirect(url_for('board'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE posts SET title = %s, content = %s WHERE id = %s", (title, content, post_id))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('board'))

    return render_template('edit_post.html', post=post)

# 댓글 수정
@app.route('/board/<int:post_id>/comment/<int:comment_id>/edit', methods=['POST'])
def edit_comment(post_id, comment_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    content = request.form['content']
    user_email = session['email']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM comments WHERE id = %s", [comment_id])
    comment = cur.fetchone()

    if comment['user_email'] != user_email:
        return redirect(url_for('view_post', post_id=post_id))

    cur.execute("UPDATE comments SET content = %s WHERE id = %s", (content, comment_id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('view_post', post_id=post_id))

# 댓글 삭제
@app.route('/board/<int:post_id>/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(post_id, comment_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    user_email = session['email']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM comments WHERE id = %s", [comment_id])
    comment = cur.fetchone()

    if comment['user_email'] != user_email:
        return redirect(url_for('view_post', post_id=post_id))

    cur.execute("DELETE FROM comments WHERE id = %s", [comment_id])
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('view_post', post_id=post_id))

@app.route('/board/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts WHERE id = %s", [post_id])
    post = cur.fetchone()
    if post['user_email'] != session['email']:
        return redirect(url_for('board'))

    cur.execute("DELETE FROM posts WHERE id = %s", [post_id])
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('board'))


@app.route('/board/new', methods=['GET', 'POST'])
def new_post():
    if not is_logged_in():
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_email = session['email']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO posts (title, content, user_email) VALUES (%s, %s, %s)", (title, content, user_email))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('board'))

    return render_template('new_post.html')


@app.route('/mypage', methods=['GET', 'POST'])
def mypage():
    if not is_logged_in():
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        email = session['email']

        # 비밀번호가 입력된 경우 암호화하여 업데이트
        if password:
            encrypted_password = sha256_crypt.encrypt(str(password))
            cur.execute("UPDATE users SET name = %s, password = %s WHERE email = %s", (name, encrypted_password, email))
        else:
            cur.execute("UPDATE users SET name = %s WHERE email = %s", (name, email))

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('mypage'))

    # 사용자 정보 가져오기
    cur.execute("SELECT * FROM users WHERE email = %s", [session['email']])
    user_info = cur.fetchone()

    # 스크랩한 기사 가져오기
    cur.execute("SELECT * FROM scraps WHERE user_email = %s", [session['email']])
    scraps = cur.fetchall()
    cur.close()

    return render_template('mypage.html', user_info=user_info, scraps=scraps, is_logged_in=is_logged_in)


users = {
    'user1': {
        'email': 'user1@example.com',
        'password': sha256_crypt.encrypt('password1'),
        'bookmarks': []
    }
    # 필요에 따라 추가 사용자 정의 가능
}

# scrap Blueprint 등록
from scrap import scrap_bp
app.register_blueprint(scrap_bp)

@app.route('/bookmark', methods=['POST'])
def bookmark():
    print("Bookmark route accessed")  # 디버그 출력
    if not is_logged_in():
        return jsonify({'status': 'fail', 'reason': 'not_logged_in'})

    data = request.json
    if not data or not 'title' in data or not 'link' in data:
        return jsonify({'status': 'fail', 'reason': 'invalid_data'})

    # MySQL scraps 테이블에 즐겨찾기 정보 저장
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO scraps (user_email, title, url) VALUES (%s, %s, %s)", (session['email'], data['title'], data['link']))
    mysql.connection.commit()
    cur.close()

    return jsonify({'status': 'success'})

# flask --debug run
if __name__ == "__main__":
    app.run(debug=True)
