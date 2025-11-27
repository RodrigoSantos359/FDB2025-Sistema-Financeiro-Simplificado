from pydantic import BaseModel
from datetime import datetime
from modules.categoria.schemas import Categoria

class TransacaoBase(BaseModel):
    valor: float
    data: datetime
    descricao: str

class TransacaoCreate(TransacaoBase):
    conta_id: int
    categoria_id: int

class TransacaoUpdate(BaseModel):
    conta_id: int | None = None
    categoria_id: int | None = None
    valor: float | None = None
    data: datetime | None = None
    descricao: str | None = None

class Transacao(TransacaoBase):
    id: int
    conta_id: int
    ativo: bool
    categoria: Categoria  # <-- AGORA VEM O OBJETO COMPLETO

    class Config:
        from_attributes = True
