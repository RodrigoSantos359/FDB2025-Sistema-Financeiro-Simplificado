import psycopg2
from psycopg2.extras import RealDictCursor
from core import settings


# 🔹 Configurações do banco (centralizadas nas settings)
DB_CONFIG = {
    "host": settings.DB_HOST,
    "database": settings.DB_NAME,
    "user": settings.DB_USER,
    "password": settings.DB_PASSWORD,
    "port": settings.DB_PORT
}


# 🔹 Classe opcional (pouco usada nas rotas, mas deixada aqui caso queira usar manualmente)
class DataBase:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

    def execute(self, sql, many=True):
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall() if many else cursor.fetchone()
        self.conn.close()
        return result

    def commit(self, sql):
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            self.conn.commit()
        self.conn.close()
        return None


# 🔹 Função de dependência para FastAPI (usada com Depends)
def get_db():
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()
