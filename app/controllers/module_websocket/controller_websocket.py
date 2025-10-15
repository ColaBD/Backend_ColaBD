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
user_sid_schemaId: dict[str, str] = {}

origins = [
  "http://localhost:4200",
  "https://colabd.onrender.com",
]

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=origins
)

async def __salvamento_agendado(sid, channel_emit: str, data: BaseTable):    
    schema_id = user_sid_schemaId[sid]
    await service_websocket.salvamento_agendado(data)
    
    full_name_channel_emit = f"{channel_emit}_{schema_id}"
    logger.info(f"🚀 dados sendo emitidos pelo canal {full_name_channel_emit}...")
    
    await sio.emit(full_name_channel_emit, data.model_dump(), skip_sid=sid)# -> colocar skip_sid=sid como ultimo parametro para quem enviou a atualização não receber a mensagem

def __create_dinamic_endpoint_name(schema_id):
    sio.on(f"create_element_{schema_id}")(create_table)
    sio.on(f"delete_element_{schema_id}")(delete_table)
    sio.on(f"update_table_atributes_{schema_id}")(update_table_atributes)
    sio.on(f"move_table_{schema_id}")(move_table)
    
@sio.event
async def connect(sid, environ, auth):
    token = auth.get("token")
    schema_id = auth.get("schema_id")

    user_id: str = get_current_user_WS(token)["id"]
    
    service_websocket.user_id = user_id
    service_websocket.schema_id = schema_id
    user_sid_schemaId[sid] = schema_id
    
    __create_dinamic_endpoint_name(schema_id)

    await service_websocket.initialie_cells()

    logger.info(f"✅ Novo usuário conectado com sid {sid}")

async def create_table(sid, new_table: dict):
    logger.info(f"📦 Criando tabela/link...")
    
    new_table_obj = CreateTable(**new_table)
    await __salvamento_agendado(sid, "receive_new_element", new_table_obj)

async def delete_table(sid, delete_table: dict):
    logger.info(f"⚠️ Deletando tabela/link...")
    
    delete_table_obj = DeleteTable(**delete_table)
    await __salvamento_agendado(sid, "receive_deleted_element", delete_table_obj)

async def update_table_atributes(sid, updated_table: dict):
    logger.info(f"🛠️ Atualizando tabela...")
    
    updated_table_obj = UpdateTable(**updated_table)
    await __salvamento_agendado(sid, "receive_updated_table", updated_table_obj)

async def move_table(sid, moved_table: dict):
    logger.info(f"👉 Movendo tabela...")
    
    moved_table_obj = MoveTable(**moved_table)
    await __salvamento_agendado(sid, "receive_moved_table", moved_table_obj)   
    
@sio.event
async def disconnect(sid):
    user_sid_schemaId.pop(sid)
    logger.info(f"⚠️ Cliente desconectado: {sid}")   