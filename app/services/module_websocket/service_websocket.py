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
        
    async def initialie_cells(self, schema_id: str, user_id: str):       
        cells_from_db = await self.service_schema.get_schema_with_cells(schema_id, user_id)
        cells_dict = cells_from_db.model_dump()

        if (schema_id not in self.pending_updates or not cells_dict["success"]):
            self.pending_updates[schema_id] = SchemaUpdates(cells=[], task=None)
            return
            
        self.pending_updates[schema_id].cells = cells_dict["data"]["cells"].copy()
            
        
    def __manipulate_create_element(self, schema_id: str, received_data: BaseElement):
        self.pending_updates[schema_id].cells.append(received_data.model_dump())
    
    def __manipulate_delete_element(self, schema_id: str, received_data: DeleteTable):
        if(len(self.pending_updates[schema_id].cells) == 0):
            return
        
        index_exclusao = 0
        for i, item in enumerate(self.pending_updates[schema_id].cells):
            if(item["id"] == received_data.id):
                index_exclusao = i
                break
                
        self.pending_updates[schema_id].cells.pop(index_exclusao)
    
    def __manipulate_update_table(self, schema_id: str, received_data: UpdateTable | TextUpdateLinkLabelAttrs):
        for item in self.pending_updates[schema_id].cells:
            if(item["id"] == received_data.id):
                if (isinstance(received_data, TextUpdateLinkLabelAttrs)):
                    item["labels"][0]["attrs"]["text"]["text"] = received_data.text
                    break
                
                item["attrs"] = received_data.attrs
                break
    
    def __manipulate_move_table(self, schema_id: str, received_data: MoveTable):
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
        if (schema_id not in self.pending_updates):
            self.pending_updates[schema_id] = SchemaUpdates()
            
        self.__preprocess_schema_received_data(schema_id, received_data) 
            
        task = self.pending_updates[schema_id].task 
        if (task):
            logger.info(f"---- Cancelando o salvamento, porque o schema foi alterado novamente ----")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # cria um multiprocess em paralelo para rodar o metodo salvamento_com_atraso por schema
        self.pending_updates[schema_id].task = asyncio.create_task(self.scheduled_save(schema_id, user_id))

    async def scheduled_save(self, schema_id: str, user_id: str):
        try:
            #enquanto não é usado redis deve esperar um determinado tempo para persistir no banco, porém caso alguem entre nesse intervalo de tempo ficará com as tabelas desatualizadas
            #quando começar a usar o redis criar um worker que irá fazer essa comunicação de pegar os dados do redis e mandar para o supabase
            await asyncio.sleep(2) 

            if(schema_id == None or schema_id.strip() == ""):
                logger.error(f"Schema ID é None, não é possível salvar o schema.")
                return
            
            if(user_id == None or user_id.strip() == ""):
                logger.error("User ID é None, não é possível salvar o schema.")
                return
            
            update_data = UpdateSchemaData(schema_id, self.pending_updates[schema_id].cells)
            await self.service_schema.update_schema(update_data, user_id)
            
            logger.info(f"Schema {schema_id} salvo no banco!")
        except asyncio.CancelledError:
            logger.info(f"Operação cancelada, pois o schema foi alterado")
            return
