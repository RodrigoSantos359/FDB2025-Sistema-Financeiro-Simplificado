from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from modules.categoria.schemas import Categoria
from modules.pessoa.schemas import Pessoa

class TransacaoBase(BaseModel):
    valor: float
    data: datetime
    descricao: str

class TransacaoCreate(TransacaoBase):
    conta_id: int
    categoria_id: int
    pessoa_id: Optional[int] = None

class TransacaoUpdate(BaseModel):
    conta_id: int | None = None
    categoria_id: int | None = None
    pessoa_id: int | None = None
    valor: float | None = None
    data: datetime | None = None
    descricao: str | None = None

class Transacao(TransacaoBase):
    id: int
    conta_id: int
    pessoa_id: Optional[int] = None
    ativo: bool
    categoria: Categoria  # <-- AGORA VEM O OBJETO COMPLETO
    pessoa: Optional[Pessoa] = None  # <-- OBJETO PESSOA COMPLETO

    class Config:
        from_attributes = True
