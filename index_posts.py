from flask import Flask, render_template
from app import mysql

app = Flask(__name__)

# MySQL 데이터베이스 연결 설정
db_connection = mysql.connector.connect(
    host="your_mysql_host",
    user="your_mysql_user",
    password="your_mysql_password",
    database="your_mysql_database"
)

# MySQL에서 게시물 데이터 가져오기
def get_posts():
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    cursor.close()
    return posts

@app.route('/')
def index():
    # 최대 3개의 게시물만 가져오기
    posts = get_posts()[:3]
    return render_template('index.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
