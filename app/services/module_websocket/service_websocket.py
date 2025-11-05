import asyncio
import logging
from app.models.entities.module_websocket.websocket import CreateTable, DeleteTable, LinkTable, MoveTable, BaseElement, TextUpdateLinkLabelAttrs, UpdateTable
from app.models.entities.module_schema.update_schema import UpdateSchemaData
from app.services.module_schema.service_schema import ServiceSchema
from app.database.module_websocket.repository_websocket import RepositoryWebsocket

logger = logging.getLogger(__name__)

class ServiceWebsocket:
    """
    Gerencia modificações de schemas via WebSocket.
    Usa Redis para armazenar células temporariamente e salva no Supabase periodicamente.
    """
    def __init__(self, service_schema: ServiceSchema, repository_websocket: RepositoryWebsocket):
        self.service_schema = service_schema
        self.repository_websocket = repository_websocket
        # Mantém apenas tasks de salvamento em memória (não as células)
        self._scheduled_tasks: dict[str, asyncio.Task] = {}
        self._locks: dict[str, asyncio.Lock] = {}       
        
    def _get_lock(self, schema_id: str) -> asyncio.Lock:
        if schema_id not in self._locks:
            self._locks[schema_id] = asyncio.Lock()

        return self._locks[schema_id]
        
    async def initialie_cells(self, schema_id: str, user_id: str):       
        """Inicializa células do schema no Redis a partir do banco de dados."""
        cells_from_db = await self.service_schema.get_schema_with_cells(schema_id, user_id)
        cells_dict = cells_from_db.model_dump()

        lock = self._get_lock(schema_id)
        async with lock:
            # Se busca falhou ou schema não existe no Redis, inicializa vazio
            if not cells_dict["success"]:
                await self.repository_websocket.set_schema_cells(schema_id, [])
                return
            
            # Verifica se já existe no Redis
            exists = await self.repository_websocket.exists_schema(schema_id)
            if not exists:
                # Carrega células do banco para Redis
                cells = cells_dict["data"]["cells"]
                await self.repository_websocket.set_schema_cells(schema_id, cells)
            
        
    async def __manipulate_create_element(self, schema_id: str, received_data: BaseElement):
        """Adiciona elemento às células no Redis. NOTA: Deve ser chamado dentro de um contexto protegido por lock."""
        cell_dict = received_data.model_dump()
        await self.repository_websocket.append_cell(schema_id, cell_dict)
    
    async def __manipulate_delete_element(self, schema_id: str, received_data: DeleteTable):
        """Remove elemento das células no Redis. NOTA: Deve ser chamado dentro de um contexto protegido por lock."""
        await self.repository_websocket.remove_cell(schema_id, received_data.id)
    
    async def __manipulate_update_table(self, schema_id: str, received_data: UpdateTable | TextUpdateLinkLabelAttrs):
        """Atualiza atributos de elemento no Redis. NOTA: Deve ser chamado dentro de um contexto protegido por lock."""
        if isinstance(received_data, TextUpdateLinkLabelAttrs):
            # Atualiza texto do label do link - precisa atualizar caminho aninhado
            # Obtém célula atual e atualiza apenas o campo necessário
            cells_result = await self.repository_websocket.get_schema_cells(schema_id)
            if cells_result.success:
                cells = cells_result.data
                for cell in cells:
                    if cell.get("id") == received_data.id:
                        if "labels" in cell and len(cell["labels"]) > 0:
                            if "attrs" in cell["labels"][0] and "text" in cell["labels"][0]["attrs"]:
                                cell["labels"][0]["attrs"]["text"]["text"] = received_data.text
                                # Salva célula atualizada
                                await self.repository_websocket.set_schema_cells(schema_id, cells)
                        break
        else:
            # Atualiza atributos da tabela
            updates = {"attrs": received_data.attrs}
            await self.repository_websocket.update_cell(schema_id, received_data.id, updates)
    
    async def __manipulate_move_table(self, schema_id: str, received_data: MoveTable):
        """Move elemento no Redis. NOTA: Deve ser chamado dentro de um contexto protegido por lock."""
        updates = {
            "position": {
                "x": received_data.position.x,
                "y": received_data.position.y
            }
        }
        await self.repository_websocket.update_cell(schema_id, received_data.id, updates)
        
    async def __preprocess_schema_received_data(self, schema_id: str, received_data: BaseElement):
        """Processa dados recebidos e aplica no Redis."""
        if (isinstance(received_data, CreateTable) or isinstance(received_data, LinkTable)):
            await self.__manipulate_create_element(schema_id, received_data)
            
        elif (isinstance(received_data, DeleteTable)):
            await self.__manipulate_delete_element(schema_id, received_data)
            
        elif (isinstance(received_data, UpdateTable) or isinstance(received_data, TextUpdateLinkLabelAttrs)):
            await self.__manipulate_update_table(schema_id, received_data)
            
        elif (isinstance(received_data, MoveTable)):
            await self.__manipulate_move_table(schema_id, received_data)

    async def manipulate_received_data(self, received_data: BaseElement, schema_id: str, user_id: str):       
        """Processa dados recebidos via WebSocket e agenda salvamento no Supabase."""
        lock = self._get_lock(schema_id)
        task_to_cancel = None
        
        async with lock:
            # Garante que schema existe no Redis
            exists = await self.repository_websocket.exists_schema(schema_id)
            if not exists:
                await self.repository_websocket.set_schema_cells(schema_id, [])

            # Aplica mudança no Redis
            await self.__preprocess_schema_received_data(schema_id, received_data) 

            # Cancela salvamento anterior se existir
            task = self._scheduled_tasks.get(schema_id)
            if task and not task.done():
                task_to_cancel = task
                task.cancel()

            # Agenda novo salvamento
            self._scheduled_tasks[schema_id] = asyncio.create_task(self.scheduled_save(schema_id, user_id))
        
        # Aguarda cancelamento fora do lock para evitar deadlock
        if task_to_cancel:
            logger.info(f"---- Cancelando o salvamento do schema {schema_id}, porque foi alterado novamente ----")
            try:
                await task_to_cancel
            except asyncio.CancelledError:
                logger.info(f"Salvamento do schema {schema_id} cancelado com sucesso")
            except Exception as e:
                logger.warning(f"Erro ao cancelar salvamento do schema {schema_id}: {e}")

    async def scheduled_save(self, schema_id: str, user_id: str):
        """Salva células do Redis no Supabase após delay."""
        try:
            # Aguarda 2 segundos antes de salvar (debounce)
            await asyncio.sleep(2) 

            if(schema_id == None or schema_id.strip() == ""):
                logger.error(f"Schema ID é None, não é possível salvar o schema.")
                return
            
            if(user_id == None or user_id.strip() == ""):
                logger.error("User ID é None, não é possível salvar o schema.")
                return

            # Lê células do Redis protegido por lock
            lock = self._get_lock(schema_id)
            async with lock:
                exists = await self.repository_websocket.exists_schema(schema_id)
                if not exists:
                    logger.warning(f"Schema {schema_id} removido antes do salvamento")
                    return
                
                # Obtém células do Redis
                cells_result = await self.repository_websocket.get_schema_cells(schema_id)
                if not cells_result.success:
                    logger.error(f"Erro ao obter células do Redis para schema {schema_id}")
                    return
                
                cells = cells_result.data
            
            # Salva no Supabase (fora do lock para não bloquear)
            update_data = UpdateSchemaData(schema_id, cells)
            await self.service_schema.update_schema(update_data, user_id)
            
            logger.info(f"Schema {schema_id} salvo no banco Supabase!")
            
        except asyncio.CancelledError:
            logger.info(f"Operação cancelada, pois o schema {schema_id} foi alterado novamente")
            return
        except Exception as e:
            logger.error(f"Erro ao salvar schema {schema_id}: {e}", exc_info=True)
