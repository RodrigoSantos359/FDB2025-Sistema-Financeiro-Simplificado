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
    # Tabela Conta
    """
CREATE TABLE IF NOT EXISTS conta (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    saldo_inicial DECIMAL(10, 2) NOT NULL DEFAULT 0,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Adicionar coluna ativo se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='conta' AND column_name='ativo') THEN
        ALTER TABLE conta ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
    END IF;
END $$;

    # 1. Tabela Categoria

    CREATE TABLE IF NOT EXISTS categoria (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('receita', 'despesa')),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- 1. Adicionar coluna ativo na tabela categoria, se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 
                   FROM information_schema.columns 
                   WHERE table_name='categoria' AND column_name='ativo') THEN
        ALTER TABLE categoria ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
    END IF;
END $$;

-- 2. Criar tabela Transacao se não existir
CREATE TABLE IF NOT EXISTS transacao (
    id SERIAL PRIMARY KEY,
    conta_id INTEGER NOT NULL REFERENCES conta(id),
    categoria_id INTEGER NOT NULL REFERENCES categoria(id),
    pessoa_id INTEGER REFERENCES pessoa(id), -- nova coluna pessoa_id
    valor DECIMAL(10, 2) NOT NULL CHECK (valor > 0),
    data DATE NOT NULL, -- alterado para DATE, sem hora
    descricao TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);


-- Adicionar coluna ativo se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='transacao' AND column_name='ativo') THEN
        ALTER TABLE transacao ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
    END IF;
END $$;


    # 3. Tabela Pessoa

    CREATE TABLE IF NOT EXISTS pessoa (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('cliente', 'fornecedor')),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Adicionar coluna ativo se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='pessoa' AND column_name='ativo') THEN
        ALTER TABLE pessoa ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
    END IF;
END $$;

    # 4. Tabela Pagamento

    CREATE TABLE IF NOT EXISTS pagamento (
    id SERIAL PRIMARY KEY,
    transacao_id INTEGER NOT NULL REFERENCES transacao(id),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pago', 'pendente', 'cancelado')),
    data_pagamento TIMESTAMP,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Adicionar coluna ativo se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='pagamento' AND column_name='ativo') THEN
        ALTER TABLE pagamento ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
    END IF;
END $$;
    );

    # 5. Índices para melhor performance

    -- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_transacao_conta_id ON transacao(conta_id);
CREATE INDEX IF NOT EXISTS idx_transacao_categoria_id ON transacao(categoria_id);
CREATE INDEX IF NOT EXISTS idx_transacao_data ON transacao(data);
CREATE INDEX IF NOT EXISTS idx_transacao_ativo ON transacao(ativo);
CREATE INDEX IF NOT EXISTS idx_pagamento_transacao_id ON pagamento(transacao_id);
CREATE INDEX IF NOT EXISTS idx_pagamento_status ON pagamento(status);
CREATE INDEX IF NOT EXISTS idx_pagamento_ativo ON pagamento(ativo);


SELECT * FROM categoria;
SELECT * FROM conta;
SELECT * FROM transacao;
ALTER TABLE transacao
ADD COLUMN pessoa_id INTEGER;  -- Ajuste o tipo se necessário
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
