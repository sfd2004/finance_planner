import sqlite3
from config import DB_PATH
from datetime import datetime, timedelta


def init_db():
    with sqlite3.connect(DB_PATH) as conn: #подключаемся к базе данных
        cursor = conn.cursor() #создание обьекта курсор 
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users ( 
            user_id INTEGER PRIMARY KEY,
            notifications_enabled BOOLEAN DEFAULT 1   
        )""")
        #создание таблицы юзерс, сохрание айди юзера
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            user_id INTEGER,
            category TEXT,
            amount INTEGER,
            current_balance INTEGER,
            PRIMARY KEY (user_id, category),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")
        #создание таблицы бюджетов, сохранение суммы бюджета и текущего баланса
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            category TEXT,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")
        conn.commit()#сохранение изменений в базе
        #создание таюлицы с доходами и расходами 

def add_user(user_id: int): #функция для добавления юзера
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,)) #если юзер уже существует то ничего не делать 
        conn.commit()


def set_budget(user_id: int, category: str, amount: int): #функция для добавления бюджета
    add_user(user_id)#проверка есть ли юзер в таблице users
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO budgets (user_id, category, amount, current_balance) 
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, category) DO UPDATE SET amount=excluded.amount
        """, (user_id, category, amount, amount))
        conn.commit()   
        #добавляем запись в таблицу бюджет, если категория уже есть то обновляем данные 


def check_current_balance(user_id: int, amount: int, category: str): #возвращает текущий бюджет 
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT current_balance FROM budgets WHERE category = ? AND user_id = ?
        """, (category, user_id))
        return cursor.fetchone()[0] 
        #достает из таблицы budgets текущее значение текущий баланс

def change_current_balance(user_id: int, amount: int, category: str, action: str): #изменение текузего баланса
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        current_balance = int(check_current_balance(user_id, amount, category))

        if action == '-':
            new_balance = current_balance - amount
        elif action == '+':
            new_balance = current_balance + amount
        # в зависимости от типа действия обновляет баланс
        cursor.execute("""
            UPDATE budgets SET current_balance = ? WHERE category = ? AND user_id = ?
        """, (new_balance, category, user_id))
        conn.commit()

def log_transaction(user_id: int, amount: int, category: str): #добавление операций в таблицу логс
    add_user(user_id)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO logs (user_id, amount, category, date)
            VALUES (?, ?, ?, ?)
        """, (user_id, amount, category, now)) #сохранение суммы, категории и даты
        conn.commit()

def get_summary(user_id: int): 
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category, current_balance, amount FROM budgets
            WHERE user_id = ?
        """, (user_id,))
        budget_data = cursor.fetchall()
        budgets = {row[0]: (row[1], row[2]) for row in budget_data}
        return budgets
#выводит текущий баланс юзера и его запланированный бюджет 

def change_notification(user_id: int, action: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET notifications_enabled = ? WHERE user_id = ?", (action, user_id,))
        conn.commit()

def get_users_for_notifications():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE notifications_enabled = 1")
        return [row[0] for row in cursor.fetchall()]

def get_daily_summary(user_id: int):
    today = datetime.now().date().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM logs
            WHERE user_id = ? AND date(date) = ?
            GROUP BY category
        """, (user_id, today))
        return cursor.fetchall()

def get_weekly_summary(user_id: int):
    start_date = (datetime.now() - timedelta(days=7)).date().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM logs
            WHERE user_id = ? AND date(date) >= ?
            GROUP BY category
        """, (user_id, start_date))
        return cursor.fetchall()