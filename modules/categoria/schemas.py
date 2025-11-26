from pydantic import BaseModel
from typing import Literal, Optional

class CategoriaCreate(BaseModel):
    nome: str
    tipo: Literal['receita', 'despesa']


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[Literal['receita', 'despesa']] = None
    ativo: Optional[bool] = None  # ← faltava isso!


class Categoria(CategoriaCreate):
    id: int
    ativo: bool = True

    class Config:
        orm_mode = True
