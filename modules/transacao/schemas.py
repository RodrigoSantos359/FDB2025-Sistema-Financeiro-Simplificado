from pydantic import BaseModel
from typing import Literal, Optional
from datetime import date


class TransacaoCreate(BaseModel):
    conta_id: int
    categoria_id: int
    valor: float
    data: date
    descricao: Optional[str] = None


class Transacao(TransacaoCreate):
    id: int
    class Config:
        orm_mode = True