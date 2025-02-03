from config.db_config import db_config
import mysql.connector
import bcrypt
from datetime import datetime
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, username, password, email=None, id=None):
        self.username = username
        self.password = password  # 将在保存时加密
        self.email = email
        self.created_at = None
        self.last_login = None
        self.id = id

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'last_login': self.last_login
        }


def create_user(username, password, email=None):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM user WHERE username = %s", (username,))
        if cursor.fetchone():
            raise ValueError("用户名已存在")

        # 加密密码
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # 插入新用户
        sql = """
        INSERT INTO user (username, password, email)
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (username, hashed_password, email))
        conn.commit()

        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def verify_user(username, password):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 查询用户
        query = "SELECT id, username, password FROM user WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        
        if result and bcrypt.checkpw(password.encode('utf-8'), result[2].encode('utf-8')):
            # 更新最后登录时间
            update_query = "UPDATE user SET last_login = NOW() WHERE id = %s"
            cursor.execute(update_query, (result[0],))
            conn.commit()
            return User(result[1], result[2], id=result[0])
        return None
        
    except Exception as e:
        print(f"Error verifying user: {str(e)}")
        return None
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_user_by_id(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            user_obj = User(user['username'], '', user['email'])
            user_obj.id = user['id']
            return user_obj
        return None
    finally:
        cursor.close()
        conn.close()

db_config = {
    'host': 'localhost',
    'user': 'root',  # 使用新创建的用户
    'password': 'root',  # 新用户的密码
    'database': 'quant4dad'
}
