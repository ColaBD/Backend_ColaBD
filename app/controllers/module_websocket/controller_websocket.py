import socketio
import logging

from app.core.auth import get_current_user_WS
from app.models.entities.module_websocket.websocket import CreateTable, DeleteTable, LinkTable, MoveTable, BaseElement, TextUpdateLinkLabelAttrs, UpdateTable
from app.services.module_schema.service_schema import ServiceSchema
from app.services.module_websocket.service_websocket import ServiceWebsocket
from app.services.module_websocket.service_lock import ServiceLock
from app.services.module_websocket.service_cursor import ServiceCursor

logger = logging.getLogger(__name__)

service_schema = ServiceSchema()
service_websocket = ServiceWebsocket(service_schema=service_schema)
service_lock = ServiceLock()
service_cursor = ServiceCursor()
user_sid_schemaId: dict[str, str] = {}
user_sid_userId: dict[str, str] = {}

origins = [
  "http://localhost:4200",
  "https://colabd.onrender.com",
]

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=origins
)

async def __salvamento_agendado(sid, event_name: str, data: BaseElement):
    schema_id = user_sid_schemaId.get(sid)
    user_id = user_sid_userId.get(sid)
    
    if not schema_id or not user_id:
        logger.warning(f"Invalid context - schema_id: {schema_id}, user_id: {user_id}")
        return
    
    await service_websocket.manipulate_received_data(data, schema_id, user_id)
    
    logger.info(f"Broadcasting event '{event_name}' to schema room '{schema_id}'")
    
    await sio.emit(
        event_name,
        data.model_dump(),
        room=schema_id,
        skip_sid=sid
    )


@sio.event
async def connect(sid, environ, auth):
    token = auth.get("token")
    schema_id = auth.get("schema_id")

    user_id: str = get_current_user_WS(token)["id"]
    
    user_sid_schemaId[sid] = schema_id
    user_sid_userId[sid] = user_id

    await sio.enter_room(sid, schema_id)
    
    await service_websocket.initialie_cells(schema_id, user_id)

    logger.info(f"User {user_id} connected to schema {schema_id} (sid: {sid}). Socket joined room '{schema_id}'")

@sio.event
async def disconnect(sid):
    schema_id = user_sid_schemaId.get(sid)
    user_id = user_sid_userId.get(sid)
    
    if schema_id and user_id:
        released_elements = await service_lock.release_all_user_locks(user_id, schema_id)
        
        if released_elements:
            for element_id in released_elements:
                await sio.emit(
                    "element_unlocked",
                    {
                        "element_id": element_id,
                        "reason": "user_disconnected"
                    },
                    room=schema_id
                )
        
        service_cursor.remove_user_all_cursors(user_id, schema_id)
        
        await sio.emit(
            "cursor_leave",
            {"user_id": user_id},
            room=schema_id
        )
        
        await sio.leave_room(sid, schema_id)
    
    user_sid_schemaId.pop(sid, None)
    user_sid_userId.pop(sid, None)
    logger.info(f"User {user_id} disconnected from schema {schema_id} (sid: {sid})")


@sio.event
async def create_element(sid, new_element: dict):
    logger.info(f"Creating table/link...")
    
    try:
        if new_element["type"] == "standard.Rectangle":
            new_element_obj = CreateTable(**new_element)
        elif new_element["type"] == "standard.Link":
            new_element_obj = LinkTable(**new_element)
        else:
            logger.warning(f"Unknown element type: {new_element['type']}")
            return
            
        await __salvamento_agendado(sid, "receive_new_element", new_element_obj)
    except Exception as e:
        logger.error(f"Error creating element: {e}")

@sio.event
async def delete_element(sid, delete_data: dict):
    logger.info(f"Deleting table/link...")
    
    try:
        delete_obj = DeleteTable(**delete_data)
        await __salvamento_agendado(sid, "receive_deleted_element", delete_obj)
    except Exception as e:
        logger.error(f"Error deleting element: {e}")

@sio.event
async def update_table_attributes(sid, updated_table: dict):
    logger.info(f"Updating table/link attributes...")
    
    try:
        if updated_table["type"] == "standard.Rectangle":
            updated_obj = UpdateTable(**updated_table)
        elif updated_table["type"] == "standard.Link":
            updated_obj = TextUpdateLinkLabelAttrs(**updated_table)
        else:
            logger.warning(f"Unknown element type: {updated_table['type']}")
            return

        await __salvamento_agendado(sid, "receive_updated_table", updated_obj)
    except Exception as e:
        logger.error(f"Error updating element: {e}")

@sio.event
async def move_table(sid, moved_table: dict):
    logger.info(f"Moving table...")
    
    try:
        moved_obj = MoveTable(**moved_table)
        await __salvamento_agendado(sid, "receive_moved_table", moved_obj)
    except Exception as e:
        logger.error(f"Error moving element: {e}")

@sio.event
async def lock_element(sid, data: dict):
    element_id = data.get("element_id")
    schema_id = user_sid_schemaId.get(sid)
    user_id = user_sid_userId.get(sid)
    
    if not element_id or not schema_id or not user_id:
        logger.warning(f"Invalid lock request - element_id: {element_id}, schema_id: {schema_id}, user_id: {user_id}")
        await sio.emit("lock_response", {
            "success": False,
            "message": "Requisição inválida"
        }, to=sid)
        return
    
    logger.info(f"Attempting to lock element {element_id} for user {user_id} in schema {schema_id}")
    
    response = await service_lock.acquire_lock(element_id, user_id, schema_id)
    
    await sio.emit("lock_response", response.model_dump(), to=sid)
    
    if response.success:
        await sio.emit(
            "element_locked",
            {
                "element_id": element_id,
                "user_id": user_id,
                "expires_at": response.expires_at.isoformat() if response.expires_at else None
            },
            room=schema_id,
            skip_sid=sid
        )

@sio.event
async def unlock_element(sid, data: dict):
    element_id = data.get("element_id")
    schema_id = user_sid_schemaId.get(sid)
    user_id = user_sid_userId.get(sid)
    
    if not element_id or not schema_id or not user_id:
        logger.warning(f"Invalid unlock request - element_id: {element_id}, schema_id: {schema_id}")
        return
    
    logger.info(f"Releasing lock for element {element_id} by user {user_id} in schema {schema_id}")
    
    response = await service_lock.release_lock(element_id, user_id, schema_id)
    
    if response.success:
        await sio.emit(
            "element_unlocked",
            {"element_id": element_id},
            room=schema_id,
            skip_sid=sid
        )

@sio.event
async def get_locked_elements(sid, data: dict):
    schema_id = user_sid_schemaId.get(sid)
    
    if not schema_id:
        logger.warning(f"Invalid get locked elements request")
        return
    
    logger.info(f"Getting locked elements for schema {schema_id}")
    
    locked_elements = await service_lock.get_schema_locks(schema_id)
    
    await sio.emit(
        "locked_elements",
        {
            "locked_elements": [elem.model_dump() for elem in locked_elements]
        },
        to=sid
    )

@sio.event
async def cursor_move(sid, data: dict):
    schema_id = user_sid_schemaId.get(sid)
    user_id = data.get("user_id")
    user_name = data.get("user_name")
    x = data.get("x")
    y = data.get("y")
    color = data.get("color")
    
    if not all([schema_id, user_id, user_name, x is not None, y is not None, color]):
        logger.warning(f"Invalid cursor move request - missing required fields")
        return
    
    logger.debug(f"Cursor move for user {user_id} in schema {schema_id}: ({x}, {y})")
    
    cursor_data = service_cursor.update_cursor(user_id, user_name, x, y, color, schema_id)
    
    await sio.emit(
        "cursor_update",
        cursor_data,
        room=schema_id,
        skip_sid=sid
    )

@sio.event
async def cursor_leave(sid, data: dict):
    schema_id = user_sid_schemaId.get(sid)
    user_id = data.get("user_id")
    
    if not schema_id or not user_id:
        logger.warning(f"Invalid cursor leave request")
        return
    
    logger.debug(f"Cursor leave for user {user_id} in schema {schema_id}")
    
    service_cursor.remove_cursor(user_id, schema_id)
    
    await sio.emit(
        "cursor_leave",
        {"user_id": user_id},
        room=schema_id,
        skip_sid=sid
    )   
