from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.module_auth.controller_auth import router as user_route
from app.controllers.module_schema.controller_schema import router as schema_route
from app.controllers.module_websocket.controller_websocket import sio 
from app.database.common.database_manager import db_manager

import logging
import socketio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('    ')

app = FastAPI( 
  title="ColaBD API",
  description="API para o desenvolvimento do ColaBD",
  version="1.0.0",
)

# uvicorn app.main:socket_app --host 0.0.0.0 --port $PORT -> novo jeito de rodar o servidor
socket_app = socketio.ASGIApp(sio, app)

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
app.include_router(schema_route)
app.include_router(sio)  
# --------------------------------

@app.on_event("startup")
async def iniciandoAPP():
  logger.info("Iniciando Aplicação...")
  await db_manager.initialize()
  logger.info("Aplicação iniciada com sucesso!")

@app.on_event("shutdown")
async def encerrandoAPP():
  logger.info("Encerrando Aplicação...")
  await db_manager.close_connections()
  logger.info("Aplicação encerrada com sucesso!")

@app.get('/', include_in_schema=False)
async def docs():
  logger.info('redirecionando para o swagger')
  return RedirectResponse(url="/docs")