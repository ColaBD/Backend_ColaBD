import socketio

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
    print(f"📦 Cliente conectado: {sid}")

@sio.event
async def disconnect(sid):
    print(f"📦 Cliente desconectado: {sid}")
    
@sio.event
async def atualizacao_schema(sid, snapshot_tabelas):
    #fazer logica para armazenar em memoria e após 10s sem mudar nada mandar para o banco
    print(f"📦 Cliente {sid} atulizou a tabela:", snapshot_tabelas)
    await sio.emit("schema_atualizado", snapshot_tabelas, skip_sid=sid)

# @sio.event
# async def criar_tabela(sid, data):
#     print(f"🟢 Cliente {sid} criou tabela:", data)
#     await sio.emit("tabela_criada", data, skip_sid=sid)

# @sio.event
# async def deletar_tabela(sid, data):
#     print(f"🔴 Cliente {sid} deletou tabela:", data)
#     await sio.emit("tabela_deletada", data, skip_sid=sid)