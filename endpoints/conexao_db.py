from flask import Flask, g
import mysql.connector

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        g.db = Conexao()
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

class Conexao:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host='db_coffeeshop',
            user='root',
            password='coffeeshop@2023',
            database='db_coffeeshop'
        )
        self.cursor = self.connection.cursor()

    def execute_query(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def close(self):
        self.cursor.close()
        self.connection.close()