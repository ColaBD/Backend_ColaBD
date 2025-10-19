from typing import TypeVar
import socketio
import logging

from app.core.auth import get_current_user_WS
from app.models.entities.module_websocket.websocket import CreateTable, DeleteTable, LinkTable, MoveTable, BaseElement, TextUpdateLinkLabelAttrs, UpdateTable
from app.services.module_schema.service_schema import ServiceSchema
from app.services.module_websocket.service_websocket import ServiceWebsocket
from app.services.module_websocket.service_lock import ServiceLock

logger = logging.getLogger(__name__)

service_schema = ServiceSchema()
service_websocket = ServiceWebsocket(service_schema=service_schema)
service_lock = ServiceLock()
user_sid_schemaId: dict[str, str] = {}

origins = [
  "http://localhost:4200",
  "https://colabd.onrender.com",
]

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=origins
)

async def __salvamento_agendado(sid, channel_emit: str, data: BaseElement):    
    schema_id = user_sid_schemaId[sid]
    await service_websocket.salvamento_agendado(data)
    
    full_name_channel_emit = f"{channel_emit}_{schema_id}"
    logger.info(f"Data being emitted through channel {full_name_channel_emit}...")
    
    await sio.emit(full_name_channel_emit, data.model_dump(), skip_sid=sid)# -> colocar skip_sid=sid como ultimo parametro para quem enviou a atualização não receber a mensagem

def __create_dinamic_endpoint_name(schema_id):
    sio.on(f"create_element_{schema_id}")(create_table)
    sio.on(f"delete_element_{schema_id}")(delete_table)
    sio.on(f"update_table_atributes_{schema_id}")(update_table_atributes)
    sio.on(f"move_table_{schema_id}")(move_table)
    sio.on(f"lock_element_{schema_id}")(lock_element)
    sio.on(f"unlock_element_{schema_id}")(unlock_element)
    sio.on(f"get_locked_elements_{schema_id}")(get_locked_elements)
    
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

    logger.info(f"New user connected with sid {sid}")

async def create_table(sid, new_element: dict):
    logger.info(f"Creating table/link...")
    
    if(new_element["type"] == "standard.Rectangle"):
        new_element_obj = CreateTable(**new_element)
    
    elif(new_element["type"] == "standard.Link"):
        new_element_obj = LinkTable(**new_element)
        
    await __salvamento_agendado(sid, "receive_new_element", new_element_obj)

async def delete_table(sid, delete_table: dict):
    logger.info(f"Deleting table/link...")
    
    delete_table_obj = DeleteTable(**delete_table)
    await __salvamento_agendado(sid, "receive_deleted_element", delete_table_obj)

async def update_table_atributes(sid, updated_table: dict):
    logger.info(f"Updating table/link...")
    
    if(updated_table["type"] == "standard.Rectangle"):
        updated_table_obj = UpdateTable(**updated_table)
    
    elif(updated_table["type"] == "standard.Link"):
        updated_table_obj = TextUpdateLinkLabelAttrs(**updated_table)

    await __salvamento_agendado(sid, "receive_updated_table", updated_table_obj)

async def move_table(sid, moved_table: dict):
    logger.info(f"Moving table...")
    
    moved_table_obj = MoveTable(**moved_table)
    await __salvamento_agendado(sid, "receive_moved_table", moved_table_obj)

async def lock_element(sid, data: dict):
    """Event handler para adquirir lock de um elemento."""
    element_id = data.get("element_id")
    schema_id = user_sid_schemaId.get(sid)
    user_id = service_websocket.user_id
    
    if not element_id or not schema_id:
        logger.warning(f"Invalid lock request - element_id: {element_id}, schema_id: {schema_id}")
        await sio.emit(f"lock_response_{schema_id}", {
            "success": False,
            "message": "Requisição inválida"
        }, to=sid)
        return
    
    logger.info(f"Attempting to lock element {element_id} for user {user_id}")
    
    # Tenta adquirir o lock
    response = await service_lock.acquire_lock(element_id, user_id, schema_id)
    
    # Envia resposta para o cliente que solicitou
    await sio.emit(f"lock_response_{schema_id}", response.model_dump(), to=sid)
    
    # Se bem-sucedido, notifica os demais clientes
    if response.success:
        await sio.emit(
            f"element_locked_{schema_id}",
            {
                "element_id": element_id,
                "user_id": user_id,
                "expires_at": response.expires_at.isoformat() if response.expires_at else None
            },
            skip_sid=sid
        )

async def unlock_element(sid, data: dict):
    """Event handler para liberar lock de um elemento."""
    element_id = data.get("element_id")
    schema_id = user_sid_schemaId.get(sid)
    user_id = service_websocket.user_id
    
    if not element_id or not schema_id:
        logger.warning(f"Invalid unlock request")
        return
    
    logger.info(f"Releasing lock for element {element_id}")
    
    # Libera o lock
    response = await service_lock.release_lock(element_id, user_id, schema_id)
    
    # Se bem-sucedido, notifica todos os clientes
    if response.success:
        await sio.emit(
            f"element_unlocked_{schema_id}",
            {"element_id": element_id},
            skip_sid=sid
        )

async def get_locked_elements(sid, data: dict):
    """Event handler para obter lista de elementos bloqueados do schema."""
    schema_id = user_sid_schemaId.get(sid)
    
    if not schema_id:
        logger.warning(f"Invalid get locked elements request")
        return
    
    logger.info(f"Getting locked elements for schema {schema_id}")
    
    # Obtém lista de locks
    locked_elements = await service_lock.get_schema_locks(schema_id)
    
    # Envia para o cliente
    await sio.emit(
        f"locked_elements_{schema_id}",
        {
            "locked_elements": [elem.model_dump() for elem in locked_elements]
        },
        to=sid
    )
    
@sio.event
async def disconnect(sid):
    schema_id = user_sid_schemaId.get(sid)
    
    if schema_id:
        user_id = service_websocket.user_id
        
        # Libera todos os locks do usuário
        released_elements = await service_lock.release_all_user_locks(user_id, schema_id)
        
        # Notifica demais clientes sobre elementos desbloqueados
        if released_elements:
            for element_id in released_elements:
                await sio.emit(
                    f"element_unlocked_{schema_id}",
                    {"element_id": element_id, "reason": "user_disconnected"}
                )
    
    user_sid_schemaId.pop(sid, None)
    logger.info(f"Client disconnected: {sid}")   