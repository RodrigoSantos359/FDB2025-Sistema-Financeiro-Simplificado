from fastapi import APIRouter, HTTPException, Depends
from typing import List
from core.db import get_db
from modules.conta.schemas import ContaCreate, Conta

router = APIRouter(prefix="/contas", tags=["contas"])

@router.get("/", response_model=List[Conta])
def list_contas(db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id, nome, saldo_inicial FROM conta ORDER BY id")
        rows = cur.fetchall()
    return rows

@router.get("/{id}", response_model=Conta)
def get_conta(id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id, nome, saldo_inicial FROM conta WHERE id = %s", (id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return row

@router.post("/", response_model=Conta)
def create_conta(payload: ContaCreate, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO conta (nome, saldo_inicial) VALUES (%s, %s) RETURNING id, nome, saldo_inicial",
            (payload.nome, payload.saldo_inicial)
        )
        row = cur.fetchone()
        db.commit()
    return row

@router.put("/{id}", response_model=Conta)
def update_conta(id: int, payload: ContaCreate, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            "UPDATE conta SET nome = %s, saldo_inicial = %s WHERE id = %s RETURNING id, nome, saldo_inicial",
            (payload.nome, payload.saldo_inicial, id)
        )
        row = cur.fetchone()
        db.commit()
    if not row:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return row

@router.delete("/{id}")
def delete_conta(id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("DELETE FROM conta WHERE id = %s RETURNING id", (id,))
        row = cur.fetchone()
        db.commit()
    if not row:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return {"detail": "Conta deletada com sucesso"}
