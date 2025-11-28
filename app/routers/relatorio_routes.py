from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from core.db import get_db, DataBase

router = APIRouter(prefix='/relatorios', tags=['relatorios'])


# Schemas para respostas dos relatórios
class Periodo(BaseModel):
    ini: str
    fim: str


class ResumoFinanceiro(BaseModel):
    periodo: Periodo
    total_receitas: float
    total_despesas: float
    saldo_final: float


class TransacaoCategoria(BaseModel):
    categoria_id: int
    nome: str
    total: float


class PagamentoPendente(BaseModel):
    id: int
    transacao_id: int
    valor: float
    data_pagamento: Optional[datetime] = None


class ContaSaldo(BaseModel):
    conta_id: int
    nome: str
    receitas: float
    despesas: float
    saldo: float


@router.get('/resumo-financeiro', response_model=ResumoFinanceiro)
def get_resumo_financeiro(
    data_ini: Optional[datetime] = Query(None, description="Data inicial (ISO 8601)"),
    data_fim: Optional[datetime] = Query(None, description="Data final (ISO 8601)"),
    conta_id: Optional[int] = Query(None, description="Filtrar por conta"),
    db: DataBase = Depends(get_db)
):
    """
    Retorna resumo financeiro com total de receitas, despesas e saldo final.
    Considera apenas transações ativas.
    """
    query = """
        SELECT 
            c.tipo,
            COALESCE(SUM(t.valor), 0) as total
        FROM transacao t
        INNER JOIN categoria c ON t.categoria_id = c.id
        WHERE t.ativo = TRUE AND c.ativo = TRUE
    """
    params = []
    
    if data_ini:
        query += " AND t.data >= %s"
        params.append(data_ini)
    
    if data_fim:
        query += " AND t.data <= %s"
        params.append(data_fim)
    
    if conta_id:
        query += " AND t.conta_id = %s"
        params.append(conta_id)
    
    query += " GROUP BY c.tipo"

    cursor = db.cursor()
    cursor.execute(query, tuple(params) if params else None)
    rows = cursor.fetchall()
    cursor.close()
    
    total_receitas = 0.0
    total_despesas = 0.0
    
    for row in rows:
        if row['tipo'] == 'receita':
            total_receitas = float(row['total'])
        elif row['tipo'] == 'despesa':
            total_despesas = float(row['total'])
    
    saldo_final = total_receitas - total_despesas
    
    periodo_ini = data_ini.strftime('%Y-%m-%d') if data_ini else None
    periodo_fim = data_fim.strftime('%Y-%m-%d') if data_fim else None
    
    return {
        "periodo": {
            "ini": periodo_ini or "",
            "fim": periodo_fim or ""
        },
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo_final": saldo_final
    }


@router.get('/transacoes-categoria', response_model=List[TransacaoCategoria])
def get_transacoes_categoria(
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoria"),
    data_ini: Optional[datetime] = Query(None, description="Data inicial (ISO 8601)"),
    data_fim: Optional[datetime] = Query(None, description="Data final (ISO 8601)"),
    db: DataBase = Depends(get_db)
):
    """
    Retorna total de transações agrupadas por categoria.
    Considera apenas transações ativas.
    """
    query = """
        SELECT 
            c.id as categoria_id,
            c.nome,
            COALESCE(SUM(t.valor), 0) as total
        FROM categoria c
        LEFT JOIN transacao t ON c.id = t.categoria_id AND t.ativo = TRUE
        WHERE c.ativo = TRUE
    """
    params = []
    
    if categoria_id:
        query += " AND c.id = %s"
        params.append(categoria_id)
    
    if data_ini:
        query += " AND (t.data IS NULL OR t.data >= %s)"
        params.append(data_ini)
    
    if data_fim:
        query += " AND (t.data IS NULL OR t.data <= %s)"
        params.append(data_fim)
    
    query += " GROUP BY c.id, c.nome HAVING COALESCE(SUM(t.valor), 0) > 0 ORDER BY total DESC"

    cursor = db.cursor()
    cursor.execute(query, tuple(params) if params else None)
    rows = cursor.fetchall()
    cursor.close()
    
    return [
        {
            "categoria_id": row['categoria_id'],
            "nome": row['nome'],
            "total": float(row['total'])
        }
        for row in rows
    ]


@router.get('/pagamentos-pendentes', response_model=List[PagamentoPendente])
def get_pagamentos_pendentes(db: DataBase = Depends(get_db)):
    """
    Retorna todos os pagamentos pendentes e ativos.
    """
    query = """
        SELECT 
            p.id,
            p.transacao_id,
            t.valor,
            p.data_pagamento
        FROM pagamento p
        INNER JOIN transacao t ON p.transacao_id = t.id
        WHERE p.status = 'pendente' 
            AND p.ativo = TRUE 
            AND t.ativo = TRUE
        ORDER BY p.id
    """

    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    
    return [
        {
            "id": row['id'],
            "transacao_id": row['transacao_id'],
            "valor": float(row['valor']),
            "data_pagamento": row['data_pagamento']
        }
        for row in rows
    ]


@router.get('/contas-saldo', response_model=List[ContaSaldo])
def get_contas_saldo(
    data_ini: Optional[datetime] = Query(None, description="Data inicial (ISO 8601)"),
    data_fim: Optional[datetime] = Query(None, description="Data final (ISO 8601)"),
    db: DataBase = Depends(get_db)
):
    """
    Retorna receitas, despesas e saldo por conta.
    Considera apenas transações ativas.
    """
    query = """
        SELECT 
            c.id as conta_id,
            c.nome,
            c.saldo_inicial,
            COALESCE(SUM(CASE WHEN cat.tipo = 'receita' THEN t.valor ELSE 0 END), 0) as receitas,
            COALESCE(SUM(CASE WHEN cat.tipo = 'despesa' THEN t.valor ELSE 0 END), 0) as despesas
        FROM conta c
        LEFT JOIN transacao t ON c.id = t.conta_id AND t.ativo = TRUE
        LEFT JOIN categoria cat ON t.categoria_id = cat.id AND cat.ativo = TRUE
        WHERE c.ativo = TRUE
    """
    params = []
    
    if data_ini:
        query += " AND (t.data IS NULL OR t.data >= %s)"
        params.append(data_ini)
    
    if data_fim:
        query += " AND (t.data IS NULL OR t.data <= %s)"
        params.append(data_fim)
    
    query += " GROUP BY c.id, c.nome, c.saldo_inicial ORDER BY c.id"

    cursor = db.cursor()
    cursor.execute(query, tuple(params) if params else None)
    rows = cursor.fetchall()
    cursor.close()
    
    return [
        {
            "conta_id": row['conta_id'],
            "nome": row['nome'],
            "receitas": float(row['receitas']),
            "despesas": float(row['despesas']),
            "saldo": float(row['saldo_inicial']) + float(row['receitas']) - float(row['despesas'])
        }
        for row in rows
    ]

