from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.module_auth.controller_auth import router as user_route

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('    ')

app = FastAPI( 
  title="ColaBD API",
  description="API para o desenvolvimento do ColaBD",
  version="1.0.0",
)

origins = [
  "http://localhost:4200",
  "https://colabd.onrender.com"
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# ---- Endpoints da aplicação ----
app.include_router(user_route)
# --------------------------------

@app.on_event("startup")
async def iniciandoAPP():
  logger.info("Iniciando Aplicação...")

@app.on_event("shutdown")
async def encerrandoAPP():
  logger.info("Encerrando Aplicação...")

@app.get('/', include_in_schema=False)
async def docs():
  logger.info('redirencionando para o swagger')
  return RedirectResponse(url="/docs")

