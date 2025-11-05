import json
import logging
from typing import Optional
from redis.asyncio import Redis
from app.models.dto.compartilhado.response import Response

logger = logging.getLogger(__name__)

class RepositoryWebsocket:
    """
    Repositório para gerenciar dados de schemas no Redis.
    Armazena células (cells) de cada schema e permite operações atômicas.
    """
    
    def __init__(self, redis_client: Redis):
        self.redis: Redis = redis_client
        # Prefixo para chaves no Redis
        self._key_prefix = "schema:"
        self._task_key_prefix = "schema:task:"
    
    def _get_cells_key(self, schema_id: str) -> str:
        """Retorna a chave Redis para células do schema."""
        return f"{self._key_prefix}{schema_id}:cells"
    
    def _get_task_key(self, schema_id: str) -> str:
        """Retorna a chave Redis para task do schema."""
        return f"{self._task_key_prefix}{schema_id}"
    
    async def get_schema_cells(self, schema_id: str) -> Response:
        """
        Obtém as células do schema do Redis.
        
        Args:
            schema_id: ID do schema
            
        Returns:
            Response com lista de células ou lista vazia se não existir
        """
        try:
            key = self._get_cells_key(schema_id)
            cells_json = await self.redis.get(key)
            
            if cells_json is None:
                return Response(data=[], success=True)
            
            # Decodifica bytes se necessário
            if isinstance(cells_json, bytes):
                cells_json = cells_json.decode('utf-8')
            
            cells = json.loads(cells_json)
            return Response(data=cells, success=True)
            
        except Exception as e:
            logger.error(f"Erro ao obter células do schema {schema_id} do Redis: {e}")
            return Response(data=str(e), success=False)
    
    async def set_schema_cells(self, schema_id: str, cells: list) -> Response:
        """
        Define as células do schema no Redis.
        
        Args:
            schema_id: ID do schema
            cells: Lista de células a serem armazenadas
            
        Returns:
            Response indicando sucesso ou falha
        """
        try:
            key = self._get_cells_key(schema_id)
            cells_json = json.dumps(cells)
            
            # Armazena com expiração de 1 hora (ajustável)
            await self.redis.setex(key, 3600, cells_json)
            
            return Response(data=True, success=True)
            
        except Exception as e:
            logger.error(f"Erro ao definir células do schema {schema_id} no Redis: {e}")
            return Response(data=str(e), success=False)
    
    async def append_cell(self, schema_id: str, cell: dict) -> Response:
        """
        Adiciona uma célula ao schema no Redis (operação atômica).
        
        Args:
            schema_id: ID do schema
            cell: Dicionário da célula a ser adicionada
            
        Returns:
            Response indicando sucesso ou falha
        """
        try:
            key = self._get_cells_key(schema_id)
            
            # Obtém células atuais
            cells_json = await self.redis.get(key)
            
            if cells_json is None:
                cells = []
            else:
                cells = json.loads(cells_json.decode('utf-8') if isinstance(cells_json, bytes) else cells_json)
            
            # Adiciona nova célula
            cells.append(cell)
            
            # Salva de volta
            await self.redis.setex(key, 3600, json.dumps(cells))
            
            return Response(data=True, success=True)
            
        except Exception as e:
            logger.error(f"Erro ao adicionar célula ao schema {schema_id} no Redis: {e}")
            return Response(data=str(e), success=False)
    
    async def remove_cell(self, schema_id: str, cell_id: str) -> Response:
        """
        Remove uma célula do schema no Redis (operação atômica).
        
        Args:
            schema_id: ID do schema
            cell_id: ID da célula a ser removida
            
        Returns:
            Response indicando sucesso ou falha
        """
        try:
            key = self._get_cells_key(schema_id)
            
            # Obtém células atuais
            cells_json = await self.redis.get(key)
            
            if cells_json is None:
                return Response(data=False, success=True)
            
            # Decodifica bytes se necessário
            if isinstance(cells_json, bytes):
                cells_json = cells_json.decode('utf-8')
            
            cells = json.loads(cells_json)
            
            # Remove célula por ID
            cells = [cell for cell in cells if cell.get("id") != cell_id]
            
            # Salva de volta
            await self.redis.setex(key, 3600, json.dumps(cells))
            
            return Response(data=True, success=True)
            
        except Exception as e:
            logger.error(f"Erro ao remover célula do schema {schema_id} no Redis: {e}")
            return Response(data=str(e), success=False)
    
    async def update_cell(self, schema_id: str, cell_id: str, updates: dict) -> Response:
        """
        Atualiza uma célula do schema no Redis (operação atômica).
        
        Args:
            schema_id: ID do schema
            cell_id: ID da célula a ser atualizada
            updates: Dicionário com campos a serem atualizados (merge recursivo)
            
        Returns:
            Response indicando sucesso ou falha
        """
        try:
            key = self._get_cells_key(schema_id)
            
            # Obtém células atuais
            cells_json = await self.redis.get(key)
            
            if cells_json is None:
                return Response(data=False, success=False)
            
            # Decodifica bytes se necessário
            if isinstance(cells_json, bytes):
                cells_json = cells_json.decode('utf-8')
            
            cells = json.loads(cells_json)
            
            # Atualiza célula por ID (merge recursivo)
            for cell in cells:
                if cell.get("id") == cell_id:
                    # Merge recursivo para atualizar campos aninhados
                    def deep_update(base_dict, update_dict):
                        for key, value in update_dict.items():
                            if isinstance(value, dict) and isinstance(base_dict.get(key), dict):
                                deep_update(base_dict[key], value)
                            else:
                                base_dict[key] = value
                    
                    deep_update(cell, updates)
                    break
            
            # Salva de volta
            await self.redis.setex(key, 3600, json.dumps(cells))
            
            return Response(data=True, success=True)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar célula do schema {schema_id} no Redis: {e}")
            return Response(data=str(e), success=False)
    
    async def delete_schema(self, schema_id: str) -> Response:
        """
        Remove todas as células do schema do Redis.
        
        Args:
            schema_id: ID do schema
            
        Returns:
            Response indicando sucesso ou falha
        """
        try:
            key = self._get_cells_key(schema_id)
            task_key = self._get_task_key(schema_id)
            
            # Remove células e task
            await self.redis.delete(key, task_key)
            
            return Response(data=True, success=True)
            
        except Exception as e:
            logger.error(f"Erro ao deletar schema {schema_id} do Redis: {e}")
            return Response(data=str(e), success=False)
    
    async def exists_schema(self, schema_id: str) -> bool:
        """
        Verifica se o schema existe no Redis.
        
        Args:
            schema_id: ID do schema
            
        Returns:
            True se existe, False caso contrário
        """
        try:
            key = self._get_cells_key(schema_id)
            exists = await self.redis.exists(key)
            return bool(exists)
        except Exception as e:
            logger.error(f"Erro ao verificar existência do schema {schema_id} no Redis: {e}")
            return False

