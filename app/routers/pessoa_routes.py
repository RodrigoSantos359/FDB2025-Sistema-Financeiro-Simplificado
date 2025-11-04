from fastapi import APIRouter, HTTPException
from typing import List
from core import db
from core.db import get_db
from modules.pessoa.schemas import PessoaCreate, Pessoa

router = APIRouter(prefix='/pessoas', tags=['pessoas'])

@router.get('/', response_model=List[Pessoa])
def list_pessoas():
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute('SELECT id, nome, tipo FROM pessoa ORDER BY id')
        rows = cur.fetchall()
    return rows

@router.get('/{id}', response_model=Pessoa)
def get_pessoa(id: int):
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute('SELECT id, nome, tipo FROM pessoa WHERE id = %s', (id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='Pessoa não encontrada')
    return row

@router.post('/', response_model=Pessoa)
def create_pessoa(payload: PessoaCreate):
    if payload.tipo not in ('cliente','fornecedor'):
        raise HTTPException(status_code=400, detail='tipo must be cliente or fornecedor')
    with db.conn.cursor() as cur:
        cur.execute(
            'INSERT INTO pessoa (nome, tipo) VALUES (%s,%s) RETURNING id, nome, tipo',
            (payload.nome, payload.tipo)
        )
        row = cur.fetchone()
    return row
