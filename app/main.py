from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import Message
from app.routers.solicitacoes import solicitacoes_controller
from app.routers.empresas import empresas_controller
from app.routers.pontos_coleta import pontos_coleta_controller
from app.routers.catadores import catadores_controller

app = FastAPI(
    title='Devs de Impacto - Backend',
    description='API para gerenciamento de solicitações de coleta'
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(solicitacoes_controller.router)
app.include_router(empresas_controller.router)
app.include_router(pontos_coleta_controller.router)
app.include_router(catadores_controller.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Server Ok'}
