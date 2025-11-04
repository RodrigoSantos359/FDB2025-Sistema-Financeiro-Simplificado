from pydantic import BaseModel
from typing import Literal

class CategoriaCreate(BaseModel):
    nome: str
    tipo: Literal['receita', 'despesa']



class Categoria(CategoriaCreate):
    id: int

    class Config:
        orm_mode = True
