import json
from fastapi import Depends
import socketio
import logging

from app.core.auth import get_current_user_WS
from app.models.entities.module_schema.update_schema import UpdateSchemaData
from app.services.module_schema.service_schema import ServiceSchema
from app.services.module_websocket.websocket_service import ServiceWebsocket

logger = logging.getLogger(__name__)

service_schema = ServiceSchema()
service_websocket = ServiceWebsocket(service_schema=service_schema)
user_dict = dict()

origins = [
  "http://localhost:4200",
  "https://colabd.onrender.com",
  "https://develop-colabd.onrender.com"
]

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=origins
)

@sio.event
async def connect(sid, environ, auth):

    token = auth.get("token")
    
    user_dict_id_email: str = get_current_user_WS(token)
    user_dict.update({"id": user_dict_id_email["id"]})

    logger.info(f"✅ Usuário {user_dict.get("id")} conectado com sid {sid}")
    # logger.error("Auth não enviado")

@sio.event
async def disconnect(sid):
    logger.info(f"📦 Cliente desconectado: {sid}")
    
@sio.event
async def atualizacao_schema(sid, snapshot_tabelas):
    service_websocket.salvamento_agendado(snapshot_tabelas, user_dict.get("id"))
        
    logger.info(f"📦 Cliente {sid} atulizou a tabela: {snapshot_tabelas}")
    await sio.emit("schema_atualizado", snapshot_tabelas)# -> colocar skip_sid=sid como ultimo parametro para quem enviou a atualização não receber a mensagem

# @sio.event
# async def criar_tabela(sid, data):
#     print(f"🟢 Cliente {sid} criou tabela:", data)
#     await sio.emit("tabela_criada", data, skip_sid=sid)

# @sio.event
# async def deletar_tabela(sid, data):
#     print(f"🔴 Cliente {sid} deletou tabela:", data)
#     await sio.emit("tabela_deletada", data, skip_sid=sid)