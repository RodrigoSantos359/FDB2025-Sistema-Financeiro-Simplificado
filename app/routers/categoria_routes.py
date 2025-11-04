from fastapi import APIRouter, HTTPException
from typing import List
from core import db
from core.db import get_db
from modules.categoria.schemas import CategoriaCreate, Categoria

router = APIRouter(prefix='/categorias', tags=['categorias'])

@router.get('/', response_model=List[Categoria])
def list_categorias():
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute('SELECT id, nome, tipo FROM categoria ORDER BY id')
        rows = cur.fetchall()
    return rows

@router.get('/{id}', response_model=Categoria)
def get_categoria(id: int):
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute('SELECT id, nome, tipo FROM categoria WHERE id = %s', (id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='Categoria não encontrada')
    return row

@router.post('/', response_model=Categoria)
def create_categoria(payload: CategoriaCreate):
    if payload.tipo not in ('receita','despesa'):
        raise HTTPException(status_code=400, detail='tipo must be receita or despesa')
    with db.conn.cursor() as cur:
        cur.execute(
            'INSERT INTO categoria (nome, tipo) VALUES (%s,%s) RETURNING id, nome, tipo',
            (payload.nome, payload.tipo)
        )
        row = cur.fetchone()
    return row
