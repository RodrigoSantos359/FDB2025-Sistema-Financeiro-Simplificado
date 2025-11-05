import sys
import os
import psycopg2

# Adiciona o diretório raiz do projeto ao path para importar `core.db`
# O diretório raiz é o que contém `core/`
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import DataBase

# Comandos SQL para criar as tabelas
# Mantendo a estrutura original de chaves primárias e estrangeiras
SQL_CREATE_TABLES = [
    # Ordem de exclusão: Tabelas dependentes primeiro
    """
    DROP TABLE IF EXISTS pagamento;
    DROP TABLE IF EXISTS transacao;
    DROP TABLE IF EXISTS conta;
    DROP TABLE IF EXISTS categoria;
    DROP TABLE IF EXISTS pessoa;
    """,
    # 1. Tabela Pessoa
    """
    CREATE TABLE IF NOT EXISTS pessoa (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('cliente', 'fornecedor'))
    );
    """,
    # 2. Tabela Conta
    """
    CREATE TABLE IF NOT EXISTS conta (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        saldo_inicial NUMERIC(10, 2) NOT NULL
    );
    """,
    # 3. Tabela Categoria
    """
    CREATE TABLE IF NOT EXISTS categoria (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        tipo VARCHAR(7) NOT NULL CHECK (tipo IN ('receita', 'despesa'))
    );
    """,
    # 4. Tabela Transacao
    """
    CREATE TABLE IF NOT EXISTS transacao (
        id SERIAL PRIMARY KEY,
        conta_id INTEGER NOT NULL REFERENCES conta(id),
        categoria_id INTEGER NOT NULL REFERENCES categoria(id),
        valor NUMERIC(10, 2) NOT NULL,
        data DATE NOT NULL,
        descricao TEXT
    );
    """,
    # 5. Tabela Pagamento
    """
    CREATE TABLE IF NOT EXISTS pagamento (
        id SERIAL PRIMARY KEY,
        transacao_id INTEGER NOT NULL REFERENCES transacao(id),
        status VARCHAR(10) NOT NULL CHECK (status IN ('pendente', 'pago', 'cancelado')),
        data_pagamento DATE
    );
    """
]

def create_tables():
    print("Conectando ao banco de dados...")
    try:
        # O DataBase.commit fecha a conexão após a execução.
        # Por isso, criamos uma nova instância para cada comando SQL.
        for sql_command in SQL_CREATE_TABLES:
            temp_db = DataBase()
            
            # Extrai a primeira linha de comando para exibição
            command_display = sql_command.strip().splitlines()[0].strip()
            print(f"Executando: {command_display}...")
            
            # O método commit é usado para rodar comandos DDL (CREATE TABLE)
            temp_db.commit(sql_command)
            
        print("Tabelas criadas com sucesso.")

    except psycopg2.OperationalError as e:
        print(f"Erro de Conexão/Operação: {e}")
        print("Certifique-se de que o servidor PostgreSQL está rodando e as configurações em core/settings.py estão corretas.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    create_tables()
