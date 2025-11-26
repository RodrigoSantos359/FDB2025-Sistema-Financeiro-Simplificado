from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from core.db import get_db, DataBase
from modules.pessoa.schemas import PessoaCreate, PessoaUpdate, Pessoa

router = APIRouter(prefix="/pessoas", tags=["pessoas"])


# =====================================================
# LISTAR PESSOAS COM FILTROS
# =====================================================
@router.get("/", response_model=List[Pessoa])
def list_pessoas(
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    tipo: Optional[str] = Query(None, description="cliente / fornecedor"),
    ativo: Optional[bool] = Query(None, description="Filtrar por ativo"),
    db: DataBase = Depends(get_db)
):
    query = """
        SELECT id, nome, tipo, ativo
        FROM pessoa
        WHERE 1 = 1
    """
    params = []

    if nome:
        query += " AND nome ILIKE %s"
        params.append(f"%{nome}%")

    if tipo:
        if tipo not in ("cliente", "fornecedor"):
            raise HTTPException(400, "Tipo inválido")
        query += " AND tipo = %s"
        params.append(tipo)

    if ativo is not None:
        query += " AND ativo = %s"
        params.append(ativo)

    query += " ORDER BY id"

    cur = db.cursor()
    cur.execute(query, tuple(params) if params else None)
    rows = cur.fetchall()
    cur.close()

    return [dict(r) for r in rows]


# =====================================================
# GET POR ID
# =====================================================
@router.get("/{id}", response_model=Pessoa)
def get_pessoa(id: int, db: DataBase = Depends(get_db)):
    cur = db.cursor()
    cur.execute(
        "SELECT id, nome, tipo, ativo FROM pessoa WHERE id = %s",
        (id,)
    )
    row = cur.fetchone()
    cur.close()

    if not row:
        raise HTTPException(404, "Pessoa não encontrada")

    return dict(row)


# =====================================================
# CRIAR PESSOA
# =====================================================
@router.post("/", response_model=Pessoa, status_code=201)
def create_pessoa(payload: PessoaCreate, db: DataBase = Depends(get_db)):

    if payload.tipo not in ("cliente", "fornecedor"):
        raise HTTPException(400, "Tipo inválido")

    cur = db.cursor()
    cur.execute(
        """
        INSERT INTO pessoa (nome, tipo, ativo)
        VALUES (%s, %s, %s)
        RETURNING id, nome, tipo, ativo
        """,
        (payload.nome, payload.tipo, True)
    )
    row = cur.fetchone()
    db.commit()
    cur.close()

    return dict(row)


# =====================================================
# UPDATE (PARCIAL OU COMPLETO)
# =====================================================
@router.put("/{id}", response_model=Pessoa)
def update_pessoa(id: int, payload: PessoaUpdate, db: DataBase = Depends(get_db)):

    cur = db.cursor()
    cur.execute("SELECT id, nome, tipo, ativo FROM pessoa WHERE id = %s", (id,))
    pessoa_atual = cur.fetchone()

    if not pessoa_atual:
        cur.close()
        raise HTTPException(404, "Pessoa não encontrada")

    updates = []
    params = []

    if payload.nome is not None:
        updates.append("nome = %s")
        params.append(payload.nome)

    if payload.tipo is not None:
        if payload.tipo not in ("cliente", "fornecedor"):
            cur.close()
            raise HTTPException(400, "Tipo inválido")
        updates.append("tipo = %s")
        params.append(payload.tipo)

    if not updates:
        cur.close()
        return dict(pessoa_atual)

    params.append(id)

    query = f"""
        UPDATE pessoa
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING id, nome, tipo, ativo
    """

    cur.execute(query, tuple(params))
    row = cur.fetchone()
    db.commit()
    cur.close()

    return dict(row)


# =====================================================
# DESATIVAR PESSOA
# =====================================================
@router.patch("/{id}/desativar", status_code=204)
def desativar_pessoa(id: int, db: DataBase = Depends(get_db)):
    cur = db.cursor()
    cur.execute(
        "UPDATE pessoa SET ativo = %s WHERE id = %s RETURNING id",
        (False, id)
    )
    row = cur.fetchone()

    if not row:
        cur.close()
        raise HTTPException(404, "Pessoa não encontrada")

    db.commit()
    cur.close()
    return None


# =====================================================
# DELETE PESSOA
# =====================================================
@router.delete("/{id}", status_code=204)
def delete_pessoa(id: int, db: DataBase = Depends(get_db)):
    cur = db.cursor()
    cur.execute("DELETE FROM pessoa WHERE id = %s RETURNING id", (id,))
    row = cur.fetchone()

    if not row:
        cur.close()
        raise HTTPException(404, "Pessoa não encontrada")

    db.commit()
    cur.close()
    return None
