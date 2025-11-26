from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from core.db import get_db
from modules.transacao.schemas import TransacaoCreate, TransacaoUpdate, Transacao

router = APIRouter(prefix="/transacoes", tags=["transacoes"])


# =======================================================
# LISTAR TRANSAÇÕES
# =======================================================
@router.get("/", response_model=List[Transacao])
def list_transacoes(
    conta_id: Optional[int] = Query(None),
    categoria_id: Optional[int] = Query(None),
    data_ini: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    ativo: Optional[bool] = Query(None),
    db=Depends(get_db)
):
    cursor = db.cursor()

    query = """
        SELECT id, conta_id, categoria_id, valor, data, descricao, ativo
        FROM transacao
        WHERE 1=1
    """

    params = []

    if conta_id:
        query += " AND conta_id = %s"
        params.append(conta_id)

    if categoria_id:
        query += " AND categoria_id = %s"
        params.append(categoria_id)

    if data_ini:
        query += " AND data >= %s"
        params.append(data_ini)

    if data_fim:
        query += " AND data <= %s"
        params.append(data_fim)

    if ativo is not None:
        query += " AND ativo = %s"
        params.append(ativo)

    query += " ORDER BY id"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    cursor.close()

    return rows  # já são dicts do RealDictCursor


# =======================================================
# GET POR ID
# =======================================================
@router.get("/{id}", response_model=Transacao)
def get_transacao(id: int, db=Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("""
        SELECT id, conta_id, categoria_id, valor, data, descricao, ativo
        FROM transacao
        WHERE id = %s
    """, (id,))

    row = cursor.fetchone()
    cursor.close()

    if not row:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    return row  # row já é dict


# =======================================================
# CRIAR TRANSAÇÃO
# =======================================================
@router.post("/", response_model=Transacao, status_code=201)
def create_transacao(payload: TransacaoCreate, db=Depends(get_db)):

    # Verifica conta
    cursor = db.cursor()
    cursor.execute("SELECT id, ativo FROM conta WHERE id = %s", (payload.conta_id,))
    conta = cursor.fetchone()
    cursor.close()

    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    if not conta["ativo"]:
        raise HTTPException(status_code=400, detail="Conta está desativada")

    # Verifica categoria
    cursor = db.cursor()
    cursor.execute("SELECT id, ativo FROM categoria WHERE id = %s", (payload.categoria_id,))
    categoria = cursor.fetchone()
    cursor.close()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    if not categoria["ativo"]:
        raise HTTPException(status_code=400, detail="Categoria desativada")

    # Inserir transação
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO transacao (conta_id, categoria_id, valor, data, descricao, ativo)
        VALUES (%s, %s, %s, %s, %s, TRUE)
        RETURNING id, conta_id, categoria_id, valor, data, descricao, ativo
    """, (payload.conta_id, payload.categoria_id, payload.valor,
          payload.data, payload.descricao))

    row = cursor.fetchone()
    db.commit()
    cursor.close()

    return row


# =======================================================
# UPDATE
# =======================================================
@router.put("/{id}", response_model=Transacao)
def update_transacao(id: int, payload: TransacaoUpdate, db=Depends(get_db)):

    # Verificar se existe
    cursor = db.cursor()
    cursor.execute("SELECT id FROM transacao WHERE id = %s", (id,))
    transacao = cursor.fetchone()
    cursor.close()

    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    updates = []
    params = []

    # Valida conta
    if payload.conta_id is not None:
        cursor = db.cursor()
        cursor.execute("SELECT id, ativo FROM conta WHERE id = %s", (payload.conta_id,))
        conta = cursor.fetchone()
        cursor.close()

        if not conta:
            raise HTTPException(status_code=404, detail="Conta não encontrada")
        if not conta["ativo"]:
            raise HTTPException(status_code=400, detail="Conta desativada")

        updates.append("conta_id = %s")
        params.append(payload.conta_id)

    # Valida categoria
    if payload.categoria_id is not None:
        cursor = db.cursor()
        cursor.execute("SELECT id, ativo FROM categoria WHERE id = %s", (payload.categoria_id,))
        categoria = cursor.fetchone()
        cursor.close()

        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        if not categoria["ativo"]:
            raise HTTPException(status_code=400, detail="Categoria desativada")

        updates.append("categoria_id = %s")
        params.append(payload.categoria_id)

    if payload.valor is not None:
        if payload.valor <= 0:
            raise HTTPException(status_code=400, detail="Valor deve ser maior que zero")
        updates.append("valor = %s")
        params.append(payload.valor)

    if payload.data is not None:
        updates.append("data = %s")
        params.append(payload.data)

    if payload.descricao is not None:
        updates.append("descricao = %s")
        params.append(payload.descricao)

    if not updates:
        return get_transacao(id, db)

    params.append(id)

    query = f"""
        UPDATE transacao
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING id, conta_id, categoria_id, valor, data, descricao, ativo
    """

    cursor = db.cursor()
    cursor.execute(query, tuple(params))
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    return row


# =======================================================
# DESATIVAR
# =======================================================
@router.patch("/{id}/desativar", status_code=204)
def desativar_transacao(id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE transacao SET ativo = FALSE WHERE id = %s RETURNING id",
        (id,)
    )
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    if not row:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    return None
