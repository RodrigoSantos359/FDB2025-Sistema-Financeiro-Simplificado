from pydantic import BaseModel
from typing import Literal, Optional
from datetime import date

StatusEnum = Literal['pendente', 'pago', 'cancelado']

class PagamentoCreate(BaseModel):
    transacao_id: int
    status: StatusEnum
    data_pagamento: Optional[date] = None


class Pagamento(PagamentoCreate):
    id: int

    class Config:
        orm_mode = True
