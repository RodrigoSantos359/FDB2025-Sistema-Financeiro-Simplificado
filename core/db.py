from sqlalchemy import create_engine
import psycopg2
from core import settings


class DataBase:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=settings.DB_HOST,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            port=settings.DB_PORT
        )

    # Nota: O método _get_conn no seu exemplo não usa as settings.
    # Removendo _get_conn e mantendo a inicialização no __init__

    def execute(self, sql, many=True):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall() if many else cursor.fetchone()
        self.conn.close()
        cursor.close()
        return result

    def commit(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        self.conn.close()
        cursor.close()
        return None # Retorna None, pois este método é para comandos que não retornam dados (DDL)

# Função para obter uma sessão do banco de dados (mantida para compatibilidade com FastAPI Depends)
def get_db():
    db = DataBase()
    try:
        yield db
    finally:
        # A classe DataBase já fecha a conexão em execute/commit, mas mantemos a estrutura
        pass
