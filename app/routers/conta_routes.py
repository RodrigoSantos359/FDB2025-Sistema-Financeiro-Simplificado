from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from core.db import get_db, DataBase
from modules.conta.schemas import ContaCreate, ContaUpdate, Conta

router = APIRouter(prefix="/contas", tags=["contas"])


# -----------------------------
# LISTAR CONTAS (com filtros)
# -----------------------------
@router.get('/', response_model=List[Conta])
def list_contas(
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    db: DataBase = Depends(get_db)
):
    query = "SELECT id, nome, saldo_inicial, ativo FROM conta WHERE 1=1"
    params = []
    
    if nome:
        query += " AND nome ILIKE %s"
        params.append(f"%{nome}%")
    
    if ativo is not None:
        query += " AND ativo = %s"
        params.append(ativo)

    query += " ORDER BY id"
    
    cursor = db.cursor()
    cursor.execute(query, tuple(params) if params else None)
    rows = cursor.fetchall()
    cursor.close()
    return rows


# -----------------------------
# OBTER CONTA POR ID
# -----------------------------
@router.get('/{id}', response_model=Conta)
def get_conta(id: int, db: DataBase = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, nome, saldo_inicial, ativo FROM conta WHERE id = %s",
        (id,)
    )
    row = cursor.fetchone()
    cursor.close()

    if not row:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    return row


# -----------------------------
# CRIAR CONTA
# -----------------------------
@router.post('/', response_model=Conta, status_code=201)
def create_conta(payload: ContaCreate, db: DataBase = Depends(get_db)):
    if payload.saldo_inicial < 0:
        raise HTTPException(status_code=400, detail='saldo_inicial deve ser maior ou igual a zero')
    
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO conta (nome, saldo_inicial, ativo) VALUES (%s, %s, %s) RETURNING id, nome, saldo_inicial, ativo",
        (payload.nome, payload.saldo_inicial, True)
    )
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    return row


# -----------------------------
# ATUALIZAR CONTA
# -----------------------------
@router.put('/{id}', response_model=Conta)
def update_conta(id: int, payload: ContaUpdate, db: DataBase = Depends(get_db)):

    # Verifica se existe
    cursor = db.cursor()
    cursor.execute("SELECT id FROM conta WHERE id = %s", (id,))
    existe = cursor.fetchone()

    if not existe:
        cursor.close()
        raise HTTPException(status_code=404, detail="Conta não encontrada")

    updates = []
    params = []

    if payload.nome is not None:
        updates.append("nome = %s")
        params.append(payload.nome)

    if payload.saldo_inicial is not None:
        if payload.saldo_inicial < 0:
            cursor.close()
            raise HTTPException(status_code=400, detail="saldo_inicial deve ser maior ou igual a zero")
        updates.append("saldo_inicial = %s")
        params.append(payload.saldo_inicial)

    if not updates:
        cursor.close()
        return get_conta(id, db)

    params.append(id)

    query = f"""
        UPDATE conta
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING id, nome, saldo_inicial, ativo
    """

    cursor.execute(query, tuple(params))
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    return row


# -----------------------------
# DESATIVAR CONTA
# -----------------------------
@router.patch("/{id}/desativar", status_code=204)
def desativar_conta(id: int, db: DataBase = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE conta SET ativo = %s WHERE id = %s RETURNING id",
        (False, id)
    )
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    if not row:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    return None


# -----------------------------
# DELETAR CONTA
# -----------------------------
@router.delete("/{id}")
def delete_conta(id: int, db: DataBase = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM conta WHERE id = %s RETURNING id", (id,))
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    if not row:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    return {"detail": "Conta deletada com sucesso"}
