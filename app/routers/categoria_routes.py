from fastapi import APIRouter, HTTPException, Depends
from typing import List
from core.db import get_db
from modules.categoria.schemas import CategoriaCreate, Categoria

router = APIRouter(prefix='/categorias', tags=['categorias'])

@router.get('/', response_model=List[Categoria])
def list_categorias(db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute('SELECT id, nome, tipo FROM categoria ORDER BY id')
        rows = cur.fetchall()
    return rows

@router.get('/{id}', response_model=Categoria)
def get_categoria(id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute('SELECT id, nome, tipo FROM categoria WHERE id = %s', (id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='Categoria não encontrada')
    return row

@router.post('/', response_model=Categoria)
def create_categoria(payload: CategoriaCreate, db=Depends(get_db)):
    if payload.tipo not in ('receita', 'despesa'):
        raise HTTPException(status_code=400, detail='tipo deve ser receita ou despesa')
    with db.cursor() as cur:
        cur.execute(
            'INSERT INTO categoria (nome, tipo) VALUES (%s, %s) RETURNING id, nome, tipo',
            (payload.nome, payload.tipo)
        )
        row = cur.fetchone()
        db.commit()
    return row

@router.put('/{id}', response_model=Categoria)
def update_categoria(id: int, payload: CategoriaCreate, db=Depends(get_db)):
    if payload.tipo not in ('receita', 'despesa'):
        raise HTTPException(status_code=400, detail='tipo deve ser receita ou despesa')
    with db.cursor() as cur:
        cur.execute(
            'UPDATE categoria SET nome = %s, tipo = %s WHERE id = %s RETURNING id, nome, tipo',
            (payload.nome, payload.tipo, id)
        )
        row = cur.fetchone()
        db.commit()
    if not row:
        raise HTTPException(status_code=404, detail='Categoria não encontrada')
    return row

@router.delete('/{id}')
def delete_categoria(id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute('DELETE FROM categoria WHERE id = %s RETURNING id', (id,))
        row = cur.fetchone()
        db.commit()
    if not row:
        raise HTTPException(status_code=404, detail='Categoria não encontrada')
    return {'detail': 'Categoria deletada com sucesso'}
