#선 실행 명령어

- pip install requests
- pip install flask mysql-connector-python

#My SQL DB 생성

-- 스키마 생성
CREATE SCHEMA IF NOT EXISTS hackathon;
USE hackathon;

-- users 테이블 생성
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nationality VARCHAR(50),
    points INT DEFAULT 0
);

-- user_policies 테이블 생성
CREATE TABLE user_policies (
    user_id INT,
    policy_code INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, policy_code)
);




