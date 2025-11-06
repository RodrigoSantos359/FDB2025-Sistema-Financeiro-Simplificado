from fastapi import APIRouter, HTTPException, Depends
from typing import List
from core.db import get_db
from modules.transacao.schemas import TransacaoCreate, Transacao

router = APIRouter(prefix="/transacoes", tags=["transacoes"])


@router.get("/", response_model=List[Transacao])
def list_transacoes(db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("""
            SELECT id, conta_id, categoria_id, valor, data, descricao
            FROM transacao
            ORDER BY id
        """)
        rows = cur.fetchall()
    return rows


@router.get("/{id}", response_model=Transacao)
def get_transacao(id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("""
            SELECT id, conta_id, categoria_id, valor, data, descricao
            FROM transacao
            WHERE id = %s
        """, (id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return row


@router.post("/", response_model=Transacao)
def create_transacao(payload: TransacaoCreate, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO transacao (conta_id, categoria_id, valor, data, descricao)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, conta_id, categoria_id, valor, data, descricao
        """, (payload.conta_id, payload.categoria_id, payload.valor, payload.data, payload.descricao))
        row = cur.fetchone()
        db.commit()
    return row


@router.put("/{id}", response_model=Transacao)
def update_transacao(id: int, payload: TransacaoCreate, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("""
            UPDATE transacao
            SET conta_id = %s, categoria_id = %s, valor = %s, data = %s, descricao = %s
            WHERE id = %s
            RETURNING id, conta_id, categoria_id, valor, data, descricao
        """, (payload.conta_id, payload.categoria_id, payload.valor, payload.data, payload.descricao, id))
        row = cur.fetchone()
        db.commit()
    if not row:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return row


@router.delete("/{id}")
def delete_transacao(id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("DELETE FROM transacao WHERE id = %s RETURNING id", (id,))
        row = cur.fetchone()
        db.commit()
    if not row:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return {"detail": "Transação deletada com sucesso"}
