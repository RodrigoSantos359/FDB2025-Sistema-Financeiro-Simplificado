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


# Função auxiliar para converter datas
def parse_date(date_str: Optional[str], field_name: str) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        raise HTTPException(400, f"{field_name} inválida. Use dd/mm/aaaa")


@router.get('/resumo-financeiro', response_model=ResumoFinanceiro)
def get_resumo_financeiro(
    data_ini: Optional[str] = Query(None, description="Data inicial (dd/mm/aaaa)"),
    data_fim: Optional[str] = Query(None, description="Data final (dd/mm/aaaa)"),
    conta_id: Optional[int] = Query(None, description="Filtrar por conta"),
    db: DataBase = Depends(get_db)
):
    data_ini_dt = parse_date(data_ini, "data_ini")
    data_fim_dt = parse_date(data_fim, "data_fim")

    query = """
        SELECT 
            c.tipo,
            COALESCE(SUM(t.valor), 0) as total
        FROM transacao t
        INNER JOIN categoria c ON t.categoria_id = c.id
        WHERE t.ativo = TRUE AND c.ativo = TRUE
    """
    params = []

    if data_ini_dt:
        query += " AND t.data >= %s"
        params.append(data_ini_dt)

    if data_fim_dt:
        query += " AND t.data <= %s"
        params.append(data_fim_dt)

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

    return {
        "periodo": {
            "ini": data_ini or "",
            "fim": data_fim or ""
        },
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo_final": saldo_final
    }


@router.get('/transacoes-categoria', response_model=List[TransacaoCategoria])
def get_transacoes_categoria(
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoria"),
    data_ini: Optional[str] = Query(None, description="Data inicial (dd/mm/aaaa)"),
    data_fim: Optional[str] = Query(None, description="Data final (dd/mm/aaaa)"),
    db: DataBase = Depends(get_db)
):
    data_ini_dt = parse_date(data_ini, "data_ini")
    data_fim_dt = parse_date(data_fim, "data_fim")

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

    if data_ini_dt:
        query += " AND (t.data IS NULL OR t.data >= %s)"
        params.append(data_ini_dt)

    if data_fim_dt:
        query += " AND (t.data IS NULL OR t.data <= %s)"
        params.append(data_fim_dt)

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
    data_ini: Optional[str] = Query(None, description="Data inicial (dd/mm/aaaa)"),
    data_fim: Optional[str] = Query(None, description="Data final (dd/mm/aaaa)"),
    db: DataBase = Depends(get_db)
):
    data_ini_dt = parse_date(data_ini, "data_ini")
    data_fim_dt = parse_date(data_fim, "data_fim")

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

    if data_ini_dt:
        query += " AND (t.data IS NULL OR t.data >= %s)"
        params.append(data_ini_dt)

    if data_fim_dt:
        query += " AND (t.data IS NULL OR t.data <= %s)"
        params.append(data_fim_dt)

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
