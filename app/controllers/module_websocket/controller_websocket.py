import socketio
from fastapi import APIRouter, WebSocket
import logging
logger = logging.getLogger(__name__)

origins = [
  "http://localhost:4200",
  "https://colabd.onrender.com"
]

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=origins
)

# route = router = APIRouter(
#     prefix="/ws",
#     tags=["WebSocket"]
# )

# @route.websocket("/atualizar_schema")
# async def atualizar_schema(websocket: WebSocket):
#     await websocket.accept()
#     await websocket.send_text("Conexão WebSocket estabelecida com sucesso!")
#     try:
#         while True:
#             data = await websocket.receive_json()
#             await websocket.send_text(f"Mensagem recebida: {data}")
#     except Exception as e:
#         print(f"Erro na conexão WebSocket: {e}")
#     finally:
#         await websocket.close()

@sio.event
async def connect(sid, environ):# environ -> dados sobre a requisição que abriu o socket
    logger.error(f"📦 Cliente conectado: {sid}")

@sio.event
async def disconnect(sid):
    logger.error(f"📦 Cliente desconectado: {sid}")
    
@sio.event
async def atualizacao_schema(sid, snapshot_tabelas):
    #fazer logica para armazenar em memoria e após 10s sem mudar nada mandar para o banco
    logger.error(f"📦 Cliente {sid} atulizou a tabela:", snapshot_tabelas)
    await sio.emit("schema_atualizado", snapshot_tabelas, skip_sid=sid)

# @sio.event
# async def criar_tabela(sid, data):
#     print(f"🟢 Cliente {sid} criou tabela:", data)
#     await sio.emit("tabela_criada", data, skip_sid=sid)

# @sio.event
# async def deletar_tabela(sid, data):
#     print(f"🔴 Cliente {sid} deletou tabela:", data)
#     await sio.emit("tabela_deletada", data, skip_sid=sid)