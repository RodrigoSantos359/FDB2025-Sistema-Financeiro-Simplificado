from fastapi import APIRouter, HTTPException
from typing import List
from core import db
from core.db import get_db
from modules.conta.schemas import ContaCreate, Conta

router = APIRouter(prefix='/contas', tags=['contas'])

@router.get('/', response_model=List[Conta])
def list_contas():
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute('SELECT id, nome, saldo_inicial FROM conta ORDER BY id')
        rows = cur.fetchall()
    return rows

@router.get('/{id}', response_model=Conta)
def get_conta(id: int):
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute('SELECT id, nome, saldo_inicial FROM conta WHERE id = %s', (id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='Conta não encontrada')
    return row

@router.post('/', response_model=Conta)
def create_conta(payload: ContaCreate):
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute(
            'INSERT INTO conta (nome, saldo_inicial) VALUES (%s,%s) RETURNING id, nome, saldo_inicial',
            (payload.nome, payload.saldo_inicial)
        )
        row = cur.fetchone()
    return row
