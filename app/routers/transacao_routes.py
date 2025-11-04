from fastapi import APIRouter, HTTPException
from typing import List
from core import db
from core.db import get_db
from modules.transacao.schemas import TransacaoCreate, Transacao

router = APIRouter(prefix='/transacoes', tags=['transacoes'])

@router.get('/', response_model=List[Transacao])
def list_transacoes():
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute('SELECT id, conta_id, categoria_id, valor, data, descricao FROM transacao ORDER BY id')
        rows = cur.fetchall()
    return rows

@router.get('/{id}', response_model=Transacao)
def get_transacao(id: int):
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute('SELECT id, conta_id, categoria_id, valor, data, descricao FROM transacao WHERE id = %s', (id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='Transacao não encontrada')
    return row

@router.post('/', response_model=Transacao)
def create_transacao(payload: TransacaoCreate):
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute(
            '''
            INSERT INTO transacao (conta_id, categoria_id, valor, data, descricao)
            VALUES (%s,%s,%s,%s,%s)
            RETURNING id, conta_id, categoria_id, valor, data, descricao
            ''',
            (payload.conta_id, payload.categoria_id, payload.valor, payload.data, payload.descricao)
        )
        row = cur.fetchone()
    return row
