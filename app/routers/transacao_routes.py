from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from core.db import get_db
from modules.transacao.schemas import TransacaoCreate, TransacaoUpdate, Transacao

router = APIRouter(prefix="/transacoes", tags=["transacoes"])

# =======================================================
# Função auxiliar para montar o objeto final
# =======================================================
def format_transacao(row):
    return {
        "id": row["id"],
        "conta_id": row["conta_id"],
        "pessoa_id": row.get("pessoa_id"),
        "valor": row["valor"],
        "data": row["data"],
        "descricao": row["descricao"],
        "ativo": row["ativo"],
        "categoria": {
            "id": row["categoria_id"],
            "nome": row["categoria_nome"],
            "tipo": row["categoria_tipo"],
            "ativo": row["categoria_ativo"]
        },
        "pessoa": {
            "id": row.get("pessoa_id"),
            "nome": row.get("pessoa_nome"),
            "tipo": row.get("pessoa_tipo"),
            "ativo": row.get("pessoa_ativo")
        } if row.get("pessoa_id") else None
    }

# =======================================================
# LISTAR TRANSAÇÕES (com filtros)
# =======================================================
@router.get("/", response_model=List[Transacao])
def list_transacoes(
    conta_id: Optional[int] = Query(None),
    categoria_id: Optional[int] = Query(None),
    data_ini: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    db=Depends(get_db)
):
    cursor = db.cursor()

    query = """
        SELECT
            t.id, t.conta_id, t.pessoa_id, t.valor, t.data, t.descricao, t.ativo,
            c.id AS categoria_id, c.nome AS categoria_nome,
            c.tipo AS categoria_tipo, c.ativo AS categoria_ativo,
            p.id AS pessoa_id, p.nome AS pessoa_nome,
            p.tipo AS pessoa_tipo, p.ativo AS pessoa_ativo
        FROM transacao t
        LEFT JOIN categoria c ON c.id = t.categoria_id
        LEFT JOIN pessoa p ON p.id = t.pessoa_id
        WHERE 1=1
    """

    params = []

    if conta_id:
        query += " AND t.conta_id = %s"
        params.append(conta_id)

    if categoria_id:
        query += " AND t.categoria_id = %s"
        params.append(categoria_id)

    if data_ini:
        try:
            data_ini_obj = datetime.strptime(data_ini, "%d/%m/%Y").date()
        except ValueError:
            data_ini_obj = datetime.strptime(data_ini, "%d-%m-%Y").date()
        query += " AND t.data >= %s"
        params.append(data_ini_obj)

    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim, "%d/%m/%Y").date()
        except ValueError:
            data_fim_obj = datetime.strptime(data_fim, "%d-%m-%Y").date()
        query += " AND t.data <= %s"
        params.append(data_fim_obj)

    if ativo is not None:
        query += " AND t.ativo = %s"
        params.append(ativo)

    query += " ORDER BY t.id"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    cursor.close()

    return [format_transacao(row) for row in rows]

# =======================================================
# GET POR ID
# =======================================================
@router.get("/{id}", response_model=Transacao)
def get_transacao(id: int, db=Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            t.id, t.conta_id, t.pessoa_id, t.valor, t.data, t.descricao, t.ativo,
            c.id AS categoria_id, c.nome AS categoria_nome,
            c.tipo AS categoria_tipo, c.ativo AS categoria_ativo,
            p.id AS pessoa_id, p.nome AS pessoa_nome,
            p.tipo AS pessoa_tipo, p.ativo AS pessoa_ativo
        FROM transacao t
        LEFT JOIN categoria c ON c.id = t.categoria_id
        LEFT JOIN pessoa p ON p.id = t.pessoa_id
        WHERE t.id = %s
    """, (id,))

    row = cursor.fetchone()
    cursor.close()

    if not row:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    return format_transacao(row)

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
    cursor.execute("SELECT id, nome, tipo, ativo FROM categoria WHERE id = %s", (payload.categoria_id,))
    categoria = cursor.fetchone()
    cursor.close()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    if not categoria["ativo"]:
        raise HTTPException(status_code=400, detail="Categoria desativada")

    # Verifica pessoa se fornecida
    pessoa = None
    if payload.pessoa_id:
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, tipo, ativo FROM pessoa WHERE id = %s", (payload.pessoa_id,))
        pessoa = cursor.fetchone()
        cursor.close()

        if not pessoa:
            raise HTTPException(status_code=404, detail="Pessoa não encontrada")
        if not pessoa["ativo"]:
            raise HTTPException(status_code=400, detail="Pessoa está desativada")

    # Inserir transação
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO transacao (conta_id, categoria_id, pessoa_id, valor, data, descricao, ativo)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        RETURNING id, conta_id, pessoa_id, valor, data, descricao, ativo
    """, (payload.conta_id, payload.categoria_id, payload.pessoa_id,
          payload.valor, payload.data, payload.descricao))  # já é datetime

    row = cursor.fetchone()
    db.commit()
    cursor.close()

    return {
        **row,
        "categoria": categoria,
        "pessoa": pessoa
    }

# =======================================================
# UPDATE
# =======================================================
@router.put("/{id}", response_model=Transacao)
def update_transacao(id: int, payload: TransacaoUpdate, db=Depends(get_db)):

    cursor = db.cursor()
    cursor.execute("SELECT id FROM transacao WHERE id = %s", (id,))
    existe = cursor.fetchone()
    cursor.close()

    if not existe:
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

    # Valida pessoa
    pessoa_atualizada = None
    if payload.pessoa_id is not None:
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, tipo, ativo FROM pessoa WHERE id = %s", (payload.pessoa_id,))
        pessoa = cursor.fetchone()
        cursor.close()

        if not pessoa:
            raise HTTPException(status_code=404, detail="Pessoa não encontrada")
        if not pessoa["ativo"]:
            raise HTTPException(status_code=400, detail="Pessoa desativada")

        pessoa_atualizada = pessoa
        updates.append("pessoa_id = %s")
        params.append(payload.pessoa_id)

    # Valida categoria
    categoria_atualizada = None
    if payload.categoria_id is not None:
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, tipo, ativo FROM categoria WHERE id = %s", (payload.categoria_id,))
        categoria = cursor.fetchone()
        cursor.close()

        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        if not categoria["ativo"]:
            raise HTTPException(status_code=400, detail="Categoria desativada")

        categoria_atualizada = categoria
        updates.append("categoria_id = %s")
        params.append(payload.categoria_id)

    if payload.valor is not None:
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
        RETURNING id, conta_id, pessoa_id, valor, data, descricao, ativo
    """

    cursor = db.cursor()
    cursor.execute(query, tuple(params))
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    # pega pessoa final
    if not pessoa_atualizada:
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, tipo, ativo FROM pessoa WHERE id = (SELECT pessoa_id FROM transacao WHERE id = %s)", (id,))
        pessoa_atualizada = cursor.fetchone()
        cursor.close()

    # pega categoria final
    if not categoria_atualizada:
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, tipo, ativo FROM categoria WHERE id = (SELECT categoria_id FROM transacao WHERE id = %s)", (id,))
        categoria_atualizada = cursor.fetchone()
        cursor.close()

    return {
        **row,
        "categoria": categoria_atualizada,
        "pessoa": pessoa_atualizada
    }

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
