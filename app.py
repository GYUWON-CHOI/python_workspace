from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from crawling import crawl_news, create_dataframe
from txt_converter import csv_to_txt
from trending import nate_crawler, list_print
from summary import summarize_files
from divide import split_news_from_file
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
import os

app = Flask(__name__)
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
    return render_template('index.html', keywords=result, is_logged_in=is_logged_in)


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

    return render_template('board.html', posts=posts, is_logged_in=is_logged_in)



@app.route('/board/<int:post_id>', methods=['GET'])
def view_post(post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts WHERE id = %s", [post_id])
    post = cur.fetchone()
    cur.close()

    return render_template('post.html', post=post)
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


@app.route('/scrap', methods=['POST'])
def scrap():
    if not is_logged_in():
        return redirect(url_for('login'))

    title = request.form['title']
    url = request.form['url']
    content = request.form['content']
    date = request.form['date']
    user_email = session['email']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO scraps (user_email, title, url, content, date) VALUES (%s, %s, %s, %s, %s)", (user_email, title, url, content, date))
    mysql.connection.commit()
    cur.close()

    return jsonify({'success': True})

@app.route('/scrap/delete/<int:scrap_id>', methods=['POST'])
def delete_scrap(scrap_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM scraps WHERE id = %s AND user_email = %s", (scrap_id, session['email']))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('mypage'))





if __name__ == "__main__":
    app.run(debug=True)
