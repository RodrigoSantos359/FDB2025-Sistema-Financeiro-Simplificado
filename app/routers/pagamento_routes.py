from fastapi import APIRouter, HTTPException
from typing import List
from core import db
from core.db import get_db
from modules.pagamento.schermas import PagamentoCreate, Pagamento

router = APIRouter(prefix='/pagamentos', tags=['pagamentos'])

@router.get('/', response_model=List[Pagamento])
def list_pagamentos():
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute('SELECT id, transacao_id, status, data_pagamento FROM pagamento ORDER BY id')
        rows = cur.fetchall()
    return rows

@router.get('/{id}', response_model=Pagamento)
def get_pagamento(id: int):
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute('SELECT id, transacao_id, status, data_pagamento FROM pagamento WHERE id = %s', (id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='Pagamento não encontrado')
    return row

@router.post('/', response_model=Pagamento)
def create_pagamento(payload: PagamentoCreate):
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute(
            'INSERT INTO pagamento (transacao_id, status, data_pagamento) VALUES (%s,%s,%s) RETURNING id, transacao_id, status, data_pagamento',
            (payload.transacao_id, payload.status, payload.data_pagamento)
        )
        row = cur.fetchone()
    return row
