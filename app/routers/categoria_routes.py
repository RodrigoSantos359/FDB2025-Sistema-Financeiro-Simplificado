from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from core.db import get_db, DataBase
from modules.categoria.schemas import CategoriaCreate, CategoriaUpdate, Categoria

router = APIRouter(prefix="/categorias", tags=["categorias"])


# ============================================================
# LISTAR CATEGORIAS COM FILTROS
# ============================================================
@router.get("/", response_model=List[Categoria])
def list_categorias(
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo (receita/despesa)"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    db: DataBase = Depends(get_db),
):
    query = "SELECT id, nome, tipo, ativo FROM categoria WHERE 1=1"
    params = []

    if nome:
        query += " AND nome ILIKE %s"
        params.append(f"%{nome}%")

    if tipo:
        if tipo not in ("receita", "despesa"):
            raise HTTPException(status_code=400, detail="tipo deve ser receita ou despesa")
        query += " AND tipo = %s"
        params.append(tipo)

    if ativo is not None:
        query += " AND ativo = %s"
        params.append(ativo)

    query += " ORDER BY id"

    cursor = db.cursor()
    cursor.execute(query, tuple(params) if params else None)
    rows = cursor.fetchall()
    cursor.close()

    return rows


# ============================================================
# GET POR ID
# ============================================================
@router.get("/{id}", response_model=Categoria)
def get_categoria(id: int, db: DataBase = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, nome, tipo, ativo FROM categoria WHERE id = %s",
        (id,),
    )
    row = cursor.fetchone()
    cursor.close()

    if not row:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    return row


# ============================================================
# CRIAR CATEGORIA
# ============================================================
@router.post("/", response_model=Categoria, status_code=201)
def create_categoria(payload: CategoriaCreate, db: DataBase = Depends(get_db)):
    if payload.tipo not in ("receita", "despesa"):
        raise HTTPException(status_code=400, detail="tipo deve ser receita ou despesa")

    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO categoria (nome, tipo, ativo)
        VALUES (%s, %s, %s)
        RETURNING id, nome, tipo, ativo
        """,
        (payload.nome, payload.tipo, True),
    )
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    return row


# ============================================================
# UPDATE COMPLETO / PARCIAL
# ============================================================
@router.put("/{id}", response_model=Categoria)
def update_categoria(id: int, payload: CategoriaUpdate, db: DataBase = Depends(get_db)):

    # Verifica se existe
    cursor = db.cursor()
    cursor.execute("SELECT id FROM categoria WHERE id = %s", (id,))
    existe = cursor.fetchone()

    if not existe:
        cursor.close()
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    updates = []
    params = []

    if payload.nome is not None:
        updates.append("nome = %s")
        params.append(payload.nome)

    if payload.tipo is not None:
        if payload.tipo not in ("receita", "despesa"):
            cursor.close()
            raise HTTPException(status_code=400, detail="tipo deve ser receita ou despesa")
        updates.append("tipo = %s")
        params.append(payload.tipo)

    if payload.ativo is not None:
        updates.append("ativo = %s")
        params.append(payload.ativo)

    if not updates:
        cursor.close()
        return get_categoria(id, db)

    params.append(id)

    query = f"""
        UPDATE categoria
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING id, nome, tipo, ativo
    """

    cursor.execute(query, tuple(params))
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    return row


# ============================================================
# DESATIVAR CATEGORIA (PATCH)
# ============================================================
@router.patch("/{id}/desativar", status_code=204)
def desativar_categoria(id: int, db: DataBase = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE categoria SET ativo = %s WHERE id = %s RETURNING id",
        (False, id),
    )
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    if not row:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    return None


# ============================================================
# DELETE
# ============================================================
@router.delete("/{id}", status_code=204)
def delete_categoria(id: int, db: DataBase = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM categoria WHERE id = %s RETURNING id",
        (id,),
    )
    row = cursor.fetchone()
    db.commit()
    cursor.close()

    if not row:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    return None
