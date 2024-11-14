from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 세션에 필요한 비밀 키 설정

# MySQL 데이터베이스 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '0111',
    'database': 'hackathon'
}

# 루트 경로: 처음 접속 시 로그인 페이지로 리다이렉트
@app.route('/')
def index():
    return redirect(url_for('login'))

# 로그인 페이지 라우팅
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and user['password_hash'] == password:  # 비밀번호 해싱 사용 시 check_password_hash로 확인 권장
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                return redirect(url_for('main'))
            else:
                return "로그인 실패: 아이디나 비밀번호가 올바르지 않습니다."

        except mysql.connector.Error as err:
            print("Error: ", err)
            return "Database connection error"

        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

# 회원가입 페이지 라우팅
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        country = request.form['country']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # 사용자 정보 삽입
            cursor.execute(
                "INSERT INTO users (username, name, password_hash, nationality, points) VALUES (%s, %s, %s, %s, %s)",
                (username, name, password, country, 0)
            )
            conn.commit()

            cursor.close()
            conn.close()

            return redirect(url_for('login'))  # 회원가입 후 로그인 페이지로 이동

        except mysql.connector.Error as err:
            print("Error: ", err)
            return "Database connection error"

    return render_template('register.html')

# 메인 페이지 라우팅 (로그인 성공 시 이동)
@app.route('/main')
def main():
    if 'user_id' in session:
        return render_template('main.html', username=session['username'])
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
