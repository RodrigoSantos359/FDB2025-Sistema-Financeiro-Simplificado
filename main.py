from fastapi import FastAPI
from app.routers.categoria_routes import router as categoria_routes
from app.routers.conta_routes import router as conta_routes
from app.routers.pessoa_routes import router as pessoa_routes
from app.routers.transacao_routes import router as transacao_routes
from app.routers.pagamento_routes import router as pagamento_routes

app = FastAPI(title='Sistema Financeiro Simplificado')

app.include_router(conta_routes)
app.include_router(categoria_routes)
app.include_router(pessoa_routes)
app.include_router(transacao_routes)
app.include_router(pagamento_routes)
