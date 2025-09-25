from typing import TypeVar
import socketio
import logging

from app.core.auth import get_current_user_WS
from app.models.entities.module_websocket.websocket import CreateTable, DeleteTable, MoveTable, BaseTable, UpdateTable
from app.services.module_schema.service_schema import ServiceSchema
from app.services.module_websocket.service_websocket import ServiceWebsocket

logger = logging.getLogger(__name__)

service_schema = ServiceSchema()
service_websocket = ServiceWebsocket(service_schema=service_schema)
user_id = ""
schema_id = ""

origins = [
  "http://localhost:4200",
  "https://colabd.onrender.com",
  "https://develop-colabd.onrender.com"
]

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=origins
)

async def __salvamento_agendado(sid, channel_emit: str, data: BaseTable):
    service_websocket.salvamento_agendado(data, user_id, schema_id)
    
    logger.info(f"📦 dados sendo emitidos...")
    await sio.emit(channel_emit, data, skip_sid=sid)# -> colocar skip_sid=sid como ultimo parametro para quem enviou a atualização não receber a mensagem

@sio.event
async def connect(sid, environ, auth):
    token = auth.get("token")
    schema_id = auth.get("schema_id")

    schema_dict_id_email: str = get_current_user_WS(token)
    user_id = schema_dict_id_email["id"]

    logger.info(f"✅ Usuário {user_id} conectado com sid {sid} e o schema id: {schema_id}")
    
@sio.event
async def create_table(sid, new_table: CreateTable):
    logger.info(f"📦 Criando tabela...")
    await __salvamento_agendado(sid, "receive_new_table", new_table)

@sio.event
async def delete_table(sid, delete_table: DeleteTable):
    logger.info(f"📦 Criando tabela...")
    await __salvamento_agendado(sid, "receive_deleted_table", delete_table)

@sio.event
async def update_table_atributes(sid, updated_table: UpdateTable):
    logger.info(f"📦 Criando tabela...")
    await __salvamento_agendado(sid, "receive_updated_table", updated_table)

@sio.event
async def move_table(sid, moved_table: MoveTable):
    logger.info(f"📦 Criando tabela...")
    await __salvamento_agendado(sid, "receive_moved_table", moved_table)   
    
@sio.event
async def disconnect(sid):
    logger.info(f"📦 Cliente desconectado: {sid}")   