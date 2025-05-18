import sqlite3
import threading

def get_top_scores(difficulty, limit=10):
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, score INTEGER, difficulty TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('SELECT score, timestamp FROM scores WHERE difficulty=? ORDER BY score DESC, timestamp ASC LIMIT ?;', (difficulty, limit))
    scores = c.fetchall()
    conn.close()
    return scores

def save_score_to_db(score, difficulty):
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, score INTEGER, difficulty TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('INSERT INTO scores (score, difficulty) VALUES (?, ?)', (score, difficulty))
    conn.commit()
    conn.close()

def save_score_async(score, difficulty):
    threading.Thread(target=save_score_to_db, args=(score, difficulty), daemon=True).start() 