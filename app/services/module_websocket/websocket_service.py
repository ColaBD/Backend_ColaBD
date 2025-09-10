import asyncio
import logging
from app.models.entities.module_schema.update_schema import UpdateSchemaData

logger = logging.getLogger(__name__)

class ServiceWebsocket:
    def __init__(self, service_schema):
        self.pending_updates = {}
        self.service_schema = service_schema

    def salvamento_agendado(self, snapshot_tabelas, user_id):
        schema_id = snapshot_tabelas["schema_id"]

        # se já tinha uma task para esse schema, cancela
        if schema_id in self.pending_updates:
            _, task = self.pending_updates[schema_id] # _ -> seria o snapshot_tabelas
            task.cancel()

        task = asyncio.create_task(self.salvamento_com_atraso(snapshot_tabelas, user_id)) # -> cria um multiprocess em paralelo para ficar rodar o metodo salvamento_com_atraso
        
        self.pending_updates[schema_id] = (snapshot_tabelas, task)

    async def salvamento_com_atraso(self, snapshot_tabelas, user_id):
        try:
            await asyncio.sleep(10) 
            
            update_data = UpdateSchemaData(snapshot_tabelas["schema_id"], snapshot_tabelas["table_info"])
            self.service_schema.update_schema(update_data, user_id)
            
            logger.info(f"💾 Schema {snapshot_tabelas['schema_id']} salvo no banco!")
        except asyncio.CancelledError:
            # foi cancelada porque chegou outra atualização antes dos 10s
            return
