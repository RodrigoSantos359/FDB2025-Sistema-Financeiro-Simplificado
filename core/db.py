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

        self.conn = None

    def _get_conn(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(
                host=settings.DB_HOST,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                port=settings.DB_PORT
            )
        return self.conn

    def execute(self, sql, params=None, many=True):
        conn = self._get_conn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(sql, params)
            result = cursor.fetchall() if many else cursor.fetchone()
            return result
        except Exception:
            # Para operações de leitura, não há necessidade de rollback
            # mas garantimos que o cursor seja fechado
            raise
        finally:
            cursor.close()

    def execute_one(self, sql, params=None):
        return self.execute(sql, params, many=False)

    def commit(self, sql, params=None):
        conn = self._get_conn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(sql, params)
            conn.commit()
            if cursor.description:
                return cursor.fetchone()
            return None
        except Exception as e:
            # Em caso de erro, fazer rollback para manter consistência
            try:
                conn.rollback()
            except Exception:
                # Se o rollback falhar, ainda assim propagamos a exceção original
                pass
            raise e
        finally:
            cursor.close()

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()


# 🔹 Função de dependência para FastAPI (usada com Depends)
def get_db():
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:

        conn.close()

