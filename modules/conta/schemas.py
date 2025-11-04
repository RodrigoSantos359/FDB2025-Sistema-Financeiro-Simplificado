from pydantic import BaseModel

class ContaCreate(BaseModel):
    nome: str
    saldo_inicial: float


class Conta(ContaCreate):
    id: int

    class Config:
        orm_mode = True
