import socketio
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

@sio.event
async def connect(sid, environ):# environ -> dados sobre a requisição que abriu o socket
    logger.info(f"📦 Cliente conectado: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"📦 Cliente desconectado: {sid}")
    
@sio.event
async def atualizacao_schema(sid, snapshot_tabelas):
    #fazer logica para armazenar em memoria e após 10s sem mudar nada mandar para o banco
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