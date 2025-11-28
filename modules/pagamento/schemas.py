from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime
from modules.transacao.schemas import Transacao

StatusEnum = Literal['pendente', 'pago', 'cancelado']

class Pagamento(BaseModel):
    id: int
    status: StatusEnum
    data_pagamento: Optional[datetime] = None
    ativo: bool = True
    transacao: Optional[Transacao] = None

    class Config:
        from_attributes = True

class PagamentoCreate(BaseModel):
    transacao_id: int
    status: StatusEnum
    data_pagamento: Optional[datetime] = None
    ativo: bool = True

class PagamentoUpdate(BaseModel):
    transacao_id: Optional[int] = None
    status: Optional[StatusEnum] = None
    data_pagamento: Optional[datetime] = None


class Pagamento(PagamentoCreate):
    id: int
    ativo: bool = True

    class Config:
        orm_mode = True
