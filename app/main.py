from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

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

# app.include_router()

@app.on_event("startup")
async def startup_event():
  logger.info("Iniciando Aplicação...")

@app.on_event("shutdown")
async def shutdown_event():
  logger.info("Encerrando Aplicação...")

@app.get('/', include_in_schema=False)
async def docs():
  logger.info('redirencionando para o swagger')
  return RedirectResponse(url="/docs")