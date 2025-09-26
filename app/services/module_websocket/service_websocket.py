import asyncio
import logging
from typing import List, Dict, Any
from app.models.entities.module_websocket.websocket import CreateTable, DeleteTable, MoveTable, BaseTable, UpdateTable
from app.models.entities.module_schema.update_schema import UpdateSchemaData
from app.services.module_schema.service_schema import ServiceSchema

logger = logging.getLogger(__name__)

class ServiceWebsocket:
    def __init__(self, service_schema: ServiceSchema):
        self.pending_updates = {}
        self.schema_body = None
        self.service_schema = service_schema
        self.cells: List[Dict[str, Any]] = []
        
    def __manipulate_create_table(self, received_data: CreateTable):
        self.cells.append(received_data.model_dump())
    
    def __manipulate_delete_table(self, received_data: DeleteTable):
        index_exclusao = 0
        for i, item in enumerate(self.cells):
            if(item.get("id") == received_data.id):
                index_exclusao = i
                break
                
        self.cells.pop(index_exclusao)
    
    def __manipulate_update_table(self, received_data: UpdateTable):
        for i, item in enumerate(self.cells):
            if(item.get("id") == received_data.id):
                item["attrs"] = received_data.attrs = received_data.attrs
                break
    
    def __manipulate_move_table(self, received_data: MoveTable):
        for i, item in enumerate(self.cells):
            if(item.get("id") == received_data.id):
                item["position"]["x"] = received_data.x
                item["position"]["y"] = received_data.y
                break
    
    def __preprocess_schema_received_data(self, received_data: BaseTable):
        if (isinstance(received_data, CreateTable)):
            self.__manipulate_create_table(received_data)
            
        elif (isinstance(received_data, DeleteTable)):
            self.__manipulate_delete_table(received_data)
            
        elif (isinstance(received_data, UpdateTable)):
            self.__manipulate_update_table(received_data)
            
        elif (isinstance(received_data, MoveTable)):
            self.__manipulate_move_table(received_data)

    def salvamento_agendado(self, received_data: BaseTable, user_id: str, schema_id: str):       
        #fazer um preprocessamento para do json do schema incluir os dados que vão vindo do websocket
        self.__preprocess_schema_received_data(received_data) 

        # se já tinha uma task para esse schema, cancela
        if (schema_id in self.pending_updates):
            _, task = self.pending_updates[schema_id] # _ -> seria o snapshot_tabelas
            task.cancel()

        task = asyncio.create_task(self.salvamento_com_atraso(user_id, schema_id)) # -> cria um multiprocess em paralelo para ficar rodar o metodo salvamento_com_atraso
        
        self.pending_updates[schema_id] = (self.cells, task)

    async def salvamento_com_atraso(self, user_id: str, schema_id: str):
        try:
            await asyncio.sleep(3) 
            
            if(schema_id == None or schema_id.strip() == ""):
                logger.error(f"Schema ID é None, não é possível salvar o schema.  ---  {schema_id}")
                return
            
            if(user_id == None or user_id.strip() == ""):
                logger.error("User ID é None, não é possível salvar o schema.")
                return
            
            if (self.cells.__len__() == 0):
                logger.error("Schema está vazio, não é possível salvar o schema.")
                return
            
            update_data = UpdateSchemaData(schema_id, self.cells)
            await self.service_schema.update_schema(update_data, user_id)
            
            logger.info(f"Schema {schema_id} salvo no banco!")
        except asyncio.CancelledError:
            logger.info(f"Operação cancelada, pois o schema foi alterado")
            return
