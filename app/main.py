from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from app.core import SECRETS

from app.controllers.module_auth.controller_auth import router as user_route

import logging

connectionString = SECRETS.CONNECTION
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('    ')

app = FastAPI( 
  title="ColaBD API",
  description="API para o desenvolvimento do ColaBD",
  version="0.0.1",
)

origins = [
  # "definir url base do front"
  "*"
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=False,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(user_route)

@app.on_event("startup")
async def iniciandoAPP():
  logger.info("Iniciando Aplicação...")
  client = MongoClient(connectionString)

  try:
    client.admin.command('ping')
    logger.info("Pinged your deployment. You successfully connected to MongoDB!")
  except Exception as e:
    logger.error(e)

@app.on_event("shutdown")
async def encerrandoAPP():
  logger.info("Encerrando Aplicação...")

@app.get('/', include_in_schema=False)
async def docs():
  logger.info('redirencionando para o swagger')
  return RedirectResponse(url="/docs")

