import asyncio
import logging
from app.models.entities.module_websocket.websocket import CreateTable, DeleteTable, LinkTable, MoveTable, BaseElement, SchemaUpdates, TextUpdateLinkLabelAttrs, UpdateTable
from app.models.entities.module_schema.update_schema import UpdateSchemaData
from app.services.module_schema.service_schema import ServiceSchema

logger = logging.getLogger(__name__)

class ServiceWebsocket:
    def __init__(self, service_schema: ServiceSchema):
        self.pending_updates: dict[str, SchemaUpdates] = {}
        self.service_schema = service_schema
        self._locks: dict[str, asyncio.Lock] = {}       
        
    def _get_lock(self, schema_id: str) -> asyncio.Lock:
        if schema_id not in self._locks:
            self._locks[schema_id] = asyncio.Lock()

        return self._locks[schema_id]
        
    async def initialie_cells(self, schema_id: str, user_id: str):       
        cells_from_db = await self.service_schema.get_schema_with_cells(schema_id, user_id)
        cells_dict = cells_from_db.model_dump()

        lock = self._get_lock(schema_id)
        async with lock:
            if (schema_id not in self.pending_updates or not cells_dict["success"]):
                self.pending_updates[schema_id] = SchemaUpdates(cells=[], task=None)
                return
                
            self.pending_updates[schema_id].cells = cells_dict["data"]["cells"].copy()
            
        
    def __manipulate_create_element(self, schema_id: str, received_data: BaseElement):
        """Adiciona elemento às células. NOTA: Deve ser chamado dentro de um contexto protegido por lock."""
        self.pending_updates[schema_id].cells.append(received_data.model_dump())
    
    def __manipulate_delete_element(self, schema_id: str, received_data: DeleteTable):
        """Remove elemento das células. NOTA: Deve ser chamado dentro de um contexto protegido por lock."""
        if(len(self.pending_updates[schema_id].cells) == 0):
            return
        
        index_exclusao = 0
        for i, item in enumerate(self.pending_updates[schema_id].cells):
            if(item["id"] == received_data.id):
                index_exclusao = i
                break
                
        self.pending_updates[schema_id].cells.pop(index_exclusao)
    
    def __manipulate_update_table(self, schema_id: str, received_data: UpdateTable | TextUpdateLinkLabelAttrs):
        """Atualiza atributos de elemento. NOTA: Deve ser chamado dentro de um contexto protegido por lock."""
        for item in self.pending_updates[schema_id].cells:
            if(item["id"] == received_data.id):
                if (isinstance(received_data, TextUpdateLinkLabelAttrs)):
                    item["labels"][0]["attrs"]["text"]["text"] = received_data.text
                    break
                
                item["attrs"] = received_data.attrs
                break
    
    def __manipulate_move_table(self, schema_id: str, received_data: MoveTable):
        """Move elemento. NOTA: Deve ser chamado dentro de um contexto protegido por lock."""
        for item in self.pending_updates[schema_id].cells:
            if(item["id"] == received_data.id):
                item["position"]["x"] = received_data.position.x
                item["position"]["y"] = received_data.position.y
                break
        
    def __preprocess_schema_received_data(self, schema_id: str, received_data: BaseElement):
        if (isinstance(received_data, CreateTable) or isinstance(received_data, LinkTable)):
            self.__manipulate_create_element(schema_id, received_data)
            
        elif (isinstance(received_data, DeleteTable)):
            self.__manipulate_delete_element(schema_id, received_data)
            
        elif (isinstance(received_data, UpdateTable) or isinstance(received_data, TextUpdateLinkLabelAttrs)):
            self.__manipulate_update_table(schema_id, received_data)
            
        elif (isinstance(received_data, MoveTable)):
            self.__manipulate_move_table(schema_id, received_data)

    async def manipulate_received_data(self, received_data: BaseElement, schema_id: str, user_id: str):       
        lock = self._get_lock(schema_id)
        task_to_cancel = None
        
        async with lock:
            if (schema_id not in self.pending_updates):
                self.pending_updates[schema_id] = SchemaUpdates()

            self.__preprocess_schema_received_data(schema_id, received_data) 

            task = self.pending_updates[schema_id].task 
            if (task):
                task_to_cancel = task
                task.cancel()

            self.pending_updates[schema_id].task = asyncio.create_task(self.scheduled_save(schema_id, user_id))
        
        if task_to_cancel:
            logger.info(f"---- Cancelando o salvamento do schema {schema_id}, porque foi alterado novamente ----")
            try:
                await task_to_cancel
            except asyncio.CancelledError:
                logger.info(f"Salvamento do schema {schema_id} cancelado com sucesso")
            except Exception as e:
                logger.warning(f"Erro ao cancelar salvamento do schema {schema_id}: {e}")

    async def scheduled_save(self, schema_id: str, user_id: str):
        try:
            # Enquanto não é usado redis deve esperar um determinado tempo para persistir no banco,
            # porém caso alguém entre nesse intervalo de tempo ficará com as tabelas desatualizadas.
            # Quando começar a usar o redis criar um worker que irá fazer essa comunicação
            # de pegar os dados do redis e mandar para o supabase
            await asyncio.sleep(2) 

            if(schema_id == None or schema_id.strip() == ""):
                logger.error(f"Schema ID é None, não é possível salvar o schema.")
                return
            
            if(user_id == None or user_id.strip() == ""):
                logger.error("User ID é None, não é possível salvar o schema.")
                return

            lock = self._get_lock(schema_id)
            async with lock:
                if schema_id not in self.pending_updates:
                    logger.warning(f"Schema {schema_id} removido antes do salvamento")
                    return
                cells_copy = self.pending_updates[schema_id].cells.copy()
            
            update_data = UpdateSchemaData(schema_id, cells_copy)
            await self.service_schema.update_schema(update_data, user_id)
            
            logger.info(f"Schema {schema_id} salvo no banco!")
        except asyncio.CancelledError:
            logger.info(f"Operação cancelada, pois o schema {schema_id} foi alterado novamente")
            return
        except Exception as e:
            logger.error(f"Erro ao salvar schema {schema_id}: {e}", exc_info=True)
