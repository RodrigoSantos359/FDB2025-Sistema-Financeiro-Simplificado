-- Script de criação/atualização do banco de dados
-- Sistema Financeiro Simplificado

-- Tabela Conta
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

-- Tabela Categoria
CREATE TABLE IF NOT EXISTS categoria (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('receita', 'despesa')),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Adicionar coluna ativo se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='categoria' AND column_name='ativo') THEN
        ALTER TABLE categoria ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
    END IF;
END $$;

-- Tabela Transacao
CREATE TABLE IF NOT EXISTS transacao (
    id SERIAL PRIMARY KEY,
    conta_id INTEGER NOT NULL REFERENCES conta(id),
    categoria_id INTEGER NOT NULL REFERENCES categoria(id),
    pessoa_id INTEGER REFERENCES pessoa(id),
    valor DECIMAL(10, 2) NOT NULL CHECK (valor > 0),
    data TIMESTAMP NOT NULL,
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

-- Tabela Pessoa
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

-- Tabela Pagamento
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

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_transacao_conta_id ON transacao(conta_id);
CREATE INDEX IF NOT EXISTS idx_transacao_categoria_id ON transacao(categoria_id);
CREATE INDEX IF NOT EXISTS idx_transacao_data ON transacao(data);
CREATE INDEX IF NOT EXISTS idx_transacao_ativo ON transacao(ativo);
CREATE INDEX IF NOT EXISTS idx_pagamento_transacao_id ON pagamento(transacao_id);
CREATE INDEX IF NOT EXISTS idx_pagamento_status ON pagamento(status);
CREATE INDEX IF NOT EXISTS idx_pagamento_ativo ON pagamento(ativo);

