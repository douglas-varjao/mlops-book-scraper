from fastapi import FastAPI
from api.routers import health, books, stats, auth, ml
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI(
    title="Public Book API - Tech Challenge",
    description="Projeto da Fase 1 da Pós-Tech em ML Engineering. API para consulta de livros, com endpoints de ML e autenticação.",
    version="1.0.0",
    contact={"name":"Douglas Varjão",
    "url":"https://github.com/douglas-varjao",
    "email":"study.viniciusvarjao@gmail.com",
    },
)

Instrumentator().instrument(app).expose(app)


app.include_router(health.router)
app.include_router(stats.router)
app.include_router(books.router)
app.include_router(auth.router)
app.include_router(ml.router)

@app.get("/", tags=["Root"])
def read_root():
    return{"message": "Welcome to the Books API! Access /docs for interactive documentation."}