from fastapi import APIRouter, HTTPException, Depends
from typing import List
from core.db import get_db
from modules.pessoa.schemas import PessoaCreate, Pessoa

router = APIRouter(prefix="/pessoas", tags=["pessoas"])


@router.get("/", response_model=List[Pessoa])
def list_pessoas(db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id, nome, tipo FROM pessoa ORDER BY id")
        rows = cur.fetchall()
    return rows


@router.get("/{id}", response_model=Pessoa)
def get_pessoa(id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id, nome, tipo FROM pessoa WHERE id = %s", (id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return row


@router.post("/", response_model=Pessoa)
def create_pessoa(payload: PessoaCreate, db=Depends(get_db)):
    if payload.tipo not in ("cliente", "fornecedor"):
        raise HTTPException(status_code=400, detail="O tipo deve ser 'cliente' ou 'fornecedor'")
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO pessoa (nome, tipo) VALUES (%s, %s) RETURNING id, nome, tipo",
            (payload.nome, payload.tipo),
        )
        row = cur.fetchone()
        db.commit()
    return row


@router.put("/{id}", response_model=Pessoa)
def update_pessoa(id: int, payload: PessoaCreate, db=Depends(get_db)):
    if payload.tipo not in ("cliente", "fornecedor"):
        raise HTTPException(status_code=400, detail="O tipo deve ser 'cliente' ou 'fornecedor'")
    with db.cursor() as cur:
        cur.execute(
            "UPDATE pessoa SET nome = %s, tipo = %s WHERE id = %s RETURNING id, nome, tipo",
            (payload.nome, payload.tipo, id),
        )
        row = cur.fetchone()
        db.commit()
    if not row:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return row


@router.delete("/{id}")
def delete_pessoa(id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("DELETE FROM pessoa WHERE id = %s RETURNING id", (id,))
        row = cur.fetchone()
        db.commit()
    if not row:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return {"detail": "Pessoa deletada com sucesso"}
