from pydantic import BaseModel
from typing import Literal


TipoPessoaEnum = Literal['cliente', 'fornecedor']

class PessoaCreate(BaseModel):
    nome: str
    tipo: TipoPessoaEnum   


class Pessoa(PessoaCreate):
    id: int

    class Config:
        orm_mode = True
