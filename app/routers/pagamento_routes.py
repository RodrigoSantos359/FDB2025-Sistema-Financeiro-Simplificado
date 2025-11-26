from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from core.db import get_db, DataBase
from modules.pagamento.schemas import PagamentoCreate, PagamentoUpdate, Pagamento

router = APIRouter(prefix="/pagamentos", tags=["pagamentos"])


# =====================================================
# LISTAR PAGAMENTOS COM FILTROS
# =====================================================
@router.get("/", response_model=List[Pagamento])
def list_pagamentos(
    transacao_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None, description="pago / pendente / cancelado"),
    data_ini: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    ativo: Optional[bool] = Query(None),
    db: DataBase = Depends(get_db)
):
    query = """
        SELECT id, transacao_id, status, data_pagamento, ativo
        FROM pagamento
        WHERE 1=1
    """
    params = []

    if transacao_id:
        query += " AND transacao_id = %s"
        params.append(transacao_id)

    if status:
        if status not in ("pago", "pendente", "cancelado"):
            raise HTTPException(400, "Status inválido")
        query += " AND status = %s"
        params.append(status)

    if data_ini:
        query += " AND data_pagamento >= %s"
        params.append(data_ini)

    if data_fim:
        query += " AND data_pagamento <= %s"
        params.append(data_fim)

    if ativo is not None:
        query += " AND ativo = %s"
        params.append(ativo)

    query += " ORDER BY id"

    cursor = db.cursor()
    cursor.execute(query, tuple(params) if params else None)
    rows = cursor.fetchall()
    cursor.close()

    return [dict(row) for row in rows]


# =====================================================
# GET POR ID
# =====================================================
@router.get("/{id}", response_model=Pagamento)
def get_pagamento(id: int, db: DataBase = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, transacao_id, status, data_pagamento, ativo FROM pagamento WHERE id = %s",
        (id,)
    )
    row = cursor.fetchone()
    cursor.close()

    if not row:
        raise HTTPException(404, "Pagamento não encontrado")

    return dict(row)


# =====================================================
# CRIAR PAGAMENTO
# =====================================================
@router.post("/", response_model=Pagamento, status_code=201)
def create_pagamento(payload: PagamentoCreate, db: DataBase = Depends(get_db)):

    if payload.status not in ("pago", "pendente", "cancelado"):
        raise HTTPException(400, "Status inválido")

    # Verificar transação
    cursor = db.cursor()
    cursor.execute("SELECT id, ativo, data FROM transacao WHERE id = %s", (payload.transacao_id,))
    transacao = cursor.fetchone()

    if not transacao:
        cursor.close()
        raise HTTPException(404, "Transação não encontrada")

    if not transacao["ativo"]:
        cursor.close()
        raise HTTPException(400, "Transação desativada")

    # Validar data
    if payload.data_pagamento and payload.data_pagamento < transacao["data"]:
        cursor.close()
        raise HTTPException(400, "data_pagamento não pode ser anterior à data da transação")

    # Inserir pagamento
    cursor.execute(
        """
        INSERT INTO pagamento (transacao_id, status, data_pagamento, ativo)
        VALUES (%s, %s, %s, %s)
        RETURNING id, transacao_id, status, data_pagamento, ativo
        """,
        (payload.transacao_id, payload.status, payload.data_pagamento, True)
    )
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    return dict(row)


# =====================================================
# UPDATE PAGAMENTO
# =====================================================
@router.put("/{id}", response_model=Pagamento)
def update_pagamento(id: int, payload: PagamentoUpdate, db: DataBase = Depends(get_db)):

    cursor = db.cursor()
    cursor.execute("SELECT * FROM pagamento WHERE id = %s", (id,))
    pagamento = cursor.fetchone()

    if not pagamento:
        cursor.close()
        raise HTTPException(404, "Pagamento não encontrado")

    updates = []
    params = []

    # Alterar transacao_id
    if payload.transacao_id is not None:
        cursor.execute("SELECT id, ativo, data FROM transacao WHERE id = %s", (payload.transacao_id,))
        transacao = cursor.fetchone()

        if not transacao:
            cursor.close()
            raise HTTPException(404, "Transação não encontrada")

        if not transacao["ativo"]:
            cursor.close()
            raise HTTPException(400, "Transação desativada")

        updates.append("transacao_id = %s")
        params.append(payload.transacao_id)

    # Alterar status
    if payload.status is not None:
        if payload.status not in ("pago", "pendente", "cancelado"):
            cursor.close()
            raise HTTPException(400, "Status inválido")

        updates.append("status = %s")
        params.append(payload.status)

    # Alterar data_pagamento
    if payload.data_pagamento is not None:

        transacao_id = payload.transacao_id or pagamento["transacao_id"]

        cursor.execute("SELECT data FROM transacao WHERE id = %s", (transacao_id,))
        transacao = cursor.fetchone()

        if transacao and payload.data_pagamento < transacao["data"]:
            cursor.close()
            raise HTTPException(400, "data_pagamento não pode ser anterior à data da transação")

        updates.append("data_pagamento = %s")
        params.append(payload.data_pagamento)

    if not updates:
        cursor.close()
        return dict(pagamento)

    params.append(id)

    query = f"""
        UPDATE pagamento
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING id, transacao_id, status, data_pagamento, ativo
    """
    cursor.execute(query, tuple(params))
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    return dict(row)


# =====================================================
# DESATIVAR PAGAMENTO
# =====================================================
@router.patch("/{id}/desativar", status_code=204)
def desativar_pagamento(id: int, db: DataBase = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE pagamento SET ativo = %s WHERE id = %s RETURNING id",
        (False, id)
    )
    row = cursor.fetchone()

    if not row:
        cursor.close()
        raise HTTPException(404, "Pagamento não encontrado")

    db.commit()
    cursor.close()
    return None
