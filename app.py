from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 세션에 필요한 비밀 키 설정

# MySQL 데이터베이스 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
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
@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # 데이터베이스 연결
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # 현재 로그인한 사용자의 포인트 업데이트 (참여 시 포인트 증가)
            user_id = session['user_id']
            cursor.execute("UPDATE users SET points = points + 250 WHERE user_id = %s", (user_id,))
            conn.commit()

        except mysql.connector.Error as err:
            print("Error: ", err)
            return "Database connection error"

        finally:
            cursor.close()
            conn.close()

    try:
        # 데이터베이스 연결
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 현재 로그인한 사용자의 포인트 조회
        user_id = session['user_id']
        cursor.execute("SELECT points FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            points = user['points']
        else:
            points = 0  # 사용자를 찾을 수 없을 경우 기본값 설정

    except mysql.connector.Error as err:
        print("Error: ", err)
        return "Database connection error"

    finally:
        cursor.close()
        conn.close()

    # main.html 렌더링 시 username과 points를 전달
    return render_template('main.html', username=session['username'], points=points)

@app.route('/store', methods=['GET', 'POST'])
def store():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        item_cost = int(request.form['item_cost'])
        try:
            # 데이터베이스 연결
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # 현재 로그인한 사용자의 포인트 조회 및 사용 처리
            user_id = session['user_id']
            cursor.execute("SELECT points FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()

            if user and user[0] >= item_cost:
                cursor.execute("UPDATE users SET points = points - %s WHERE user_id = %s", (item_cost, user_id))
                conn.commit()
                message = "교환이 완료되었습니다!"
            else:
                message = "포인트가 부족합니다."

        except mysql.connector.Error as err:
            print("Error: ", err)
            return "Database connection error"

        finally:
            cursor.close()
            conn.close()

        return render_template('store.html', username=session['username'], points=user[0] - item_cost if user and user[0] >= item_cost else user[0], message=message)

    try:
        # 데이터베이스 연결
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 현재 로그인한 사용자의 포인트 조회
        user_id = session['user_id']
        cursor.execute("SELECT points FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            points = user['points']
        else:
            points = 0  # 사용자를 찾을 수 없을 경우 기본값 설정

    except mysql.connector.Error as err:
        print("Error: ", err)
        return "Database connection error"

    finally:
        cursor.close()
        conn.close()

    # store.html 렌더링 시 username과 points를 전달
    return render_template('store.html', username=session['username'], points=points)

# 뉴스 페이지 라우팅
@app.route('/news')
def news():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        # 데이터베이스 연결
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 현재 로그인한 사용자의 포인트 조회
        user_id = session['user_id']
        cursor.execute("SELECT points FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            points = user['points']
        else:
            points = 0  # 사용자를 찾을 수 없을 경우 기본값 설정

    except mysql.connector.Error as err:
        print("Error: ", err)
        return "Database connection error"

    finally:
        cursor.close()
        conn.close()

    # news.html 렌더링 시 username과 points를 전달
    return render_template('news.html', username=session['username'], points=points)

if __name__ == '__main__':
    app.run(debug=True)
