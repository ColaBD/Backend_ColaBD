import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from app.models.entities.module_websocket.websocket import Lock, LockResponse, LockedElement

logger = logging.getLogger(__name__)


class ServiceLock:
    """
    Serviço para gerenciar locks colaborativos em tempo real.
    
    Cada elemento em um schema pode ter apenas um lock por vez.
    Os locks expiram automaticamente após um período de inatividade (TTL).
    """
    
    # Armazenamento: {schema_id: {element_id: Lock}}
    _locks: Dict[str, Dict[str, Lock]] = {}
    
    # Armazenamento de usuários por schema para limpeza de locks
    # {schema_id: {user_id: {element_ids}}}
    _user_elements: Dict[str, Dict[str, set]] = {}
    
    # Tasks de limpeza de locks expirados por schema
    _cleanup_tasks: Dict[str, asyncio.Task] = {}
    
    TTL_SECONDS = 30  # Time-to-live padrão para locks
    CLEANUP_INTERVAL = 5  # Intervalo de verificação de locks expirados
    
    def __init__(self):
        """Inicializa o serviço de lock."""
        pass
    
    async def initialize_schema(self, schema_id: str) -> None:
        """
        Inicializa tracking para um novo schema.
        Inicia task de limpeza automática de locks expirados.
        """
        if schema_id not in self._locks:
            self._locks[schema_id] = {}
            self._user_elements[schema_id] = {}
            
            # Inicia task de limpeza automática
            if schema_id not in self._cleanup_tasks:
                self._cleanup_tasks[schema_id] = asyncio.create_task(
                    self._cleanup_expired_locks(schema_id)
                )
                logger.info(f"Automatic lock cleanup started for schema {schema_id}")
    
    async def acquire_lock(
        self, 
        element_id: str, 
        user_id: str, 
        schema_id: str, 
        ttl_seconds: int = TTL_SECONDS
    ) -> LockResponse:
        """
        Tenta adquirir um lock para um elemento.
        
        Args:
            element_id: ID do elemento a ser lockado
            user_id: ID do usuário que quer fazer o lock
            schema_id: ID do schema
            ttl_seconds: Tempo de vida do lock em segundos
            
        Returns:
            LockResponse com o resultado da operação
        """
        await self.initialize_schema(schema_id)
        
        element_locks = self._locks[schema_id]
        
        # Verifica se elemento já tem lock
        if element_id in element_locks:
            existing_lock = element_locks[element_id]
            
            # Se lock expirou, remove
            if existing_lock.is_expired():
                logger.info(f"Expired lock for element {element_id}, removing...")
                await self.release_lock(element_id, existing_lock.user_id, schema_id)
                # Tenta novamente após remover lock expirado
                return await self.acquire_lock(element_id, user_id, schema_id, ttl_seconds)
            
            # Se lock é do mesmo usuário, renova
            if existing_lock.user_id == user_id:
                existing_lock.refresh(ttl_seconds)
                logger.info(f"Lock renewed for element {element_id} by user {user_id}")
                return LockResponse(
                    success=True,
                    element_id=element_id,
                    user_id=user_id,
                    locked_by_user=True,
                    message="Lock renovado com sucesso",
                    expires_at=existing_lock.expires_at
                )
            
            # Lock é de outro usuário
            logger.info(f"Element {element_id} already locked by {existing_lock.user_id}")
            return LockResponse(
                success=False,
                element_id=element_id,
                user_id=existing_lock.user_id,
                locked_by_user=False,
                message=f"Elemento já está sendo editado por outro usuário",
                expires_at=existing_lock.expires_at
            )
        
        # Cria novo lock
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        new_lock = Lock(
            element_id=element_id,
            user_id=user_id,
            schema_id=schema_id,
            expires_at=expires_at
        )
        
        element_locks[element_id] = new_lock
        
        # Registra elemento no usuário para limpeza posterior
        if user_id not in self._user_elements[schema_id]:
            self._user_elements[schema_id][user_id] = set()
        self._user_elements[schema_id][user_id].add(element_id)
        
        logger.info(f"Lock acquired for element {element_id} by user {user_id}")
        return LockResponse(
            success=True,
            element_id=element_id,
            user_id=user_id,
            locked_by_user=True,
            message="Lock adquirido com sucesso",
            expires_at=expires_at
        )
    
    async def release_lock(
        self, 
        element_id: str, 
        user_id: str, 
        schema_id: str
    ) -> LockResponse:
        """
        Libera um lock de um elemento.
        
        Args:
            element_id: ID do elemento
            user_id: ID do usuário que detém o lock
            schema_id: ID do schema
            
        Returns:
            LockResponse com o resultado
        """
        await self.initialize_schema(schema_id)
        
        element_locks = self._locks[schema_id]
        
        if element_id not in element_locks:
            logger.warning(f"Attempt to release non-existent lock for element {element_id}")
            return LockResponse(
                success=False,
                element_id=element_id,
                user_id=user_id,
                locked_by_user=False,
                message="Lock não existe ou já foi liberado"
            )
        
        lock = element_locks[element_id]
        
        # Verifica se o usuário que está tentando liberar é o proprietário
        if lock.user_id != user_id:
            logger.warning(
                f"User {user_id} attempted to release lock of {element_id} owned by {lock.user_id}"
            )
            return LockResponse(
                success=False,
                element_id=element_id,
                user_id=lock.user_id,
                locked_by_user=False,
                message="Apenas o usuário que detém o lock pode liberá-lo"
            )
        
        # Remove o lock
        del element_locks[element_id]
        
        # Remove do rastreamento de usuário
        if user_id in self._user_elements[schema_id]:
            self._user_elements[schema_id][user_id].discard(element_id)
        
        logger.info(f"Lock released for element {element_id}")
        return LockResponse(
            success=True,
            element_id=element_id,
            user_id=user_id,
            locked_by_user=True,
            message="Lock liberado com sucesso"
        )
    
    async def get_lock_info(
        self, 
        element_id: str, 
        user_id: str,
        schema_id: str
    ) -> Optional[LockedElement]:
        """
        Obtém informações sobre o lock de um elemento.
        
        Returns:
            LockedElement se estiver lockado, None caso contrário
        """
        if schema_id not in self._locks:
            return None
        
        element_locks = self._locks[schema_id]
        
        if element_id not in element_locks:
            return None
        
        lock = element_locks[element_id]
        
        # Verifica se expirou
        if lock.is_expired():
            await self.release_lock(element_id, lock.user_id, schema_id)
            return None
        
        return LockedElement(
            element_id=element_id,
            user_id=lock.user_id,
            locked_by_user=lock.user_id == user_id,
            expires_at=lock.expires_at
        )
    
    async def get_schema_locks(self, schema_id: str) -> list[LockedElement]:
        """
        Obtém todos os locks ativos de um schema.
        
        Returns:
            Lista de elementos bloqueados
        """
        if schema_id not in self._locks:
            return []
        
        element_locks = self._locks[schema_id]
        locked_elements = []
        
        expired_locks = []
        for element_id, lock in element_locks.items():
            if lock.is_expired():
                expired_locks.append((element_id, lock.user_id, schema_id))
            else:
                locked_elements.append(LockedElement(
                    element_id=element_id,
                    user_id=lock.user_id,
                    locked_by_user=False,
                    expires_at=lock.expires_at
                ))
        
        # Remove locks expirados
        for element_id, user_id, schema_id in expired_locks:
            await self.release_lock(element_id, user_id, schema_id)
        
        return locked_elements
    
    async def release_all_user_locks(
        self, 
        user_id: str, 
        schema_id: str
    ) -> list[str]:
        """
        Libera todos os locks de um usuário em um schema.
        Chamado quando usuário se desconecta.
        
        Returns:
            Lista de element_ids que foram desbloqueados
        """
        if schema_id not in self._user_elements:
            return []
        
        if user_id not in self._user_elements[schema_id]:
            return []
        
        element_ids = list(self._user_elements[schema_id][user_id])
        released_elements = []
        
        for element_id in element_ids:
            response = await self.release_lock(element_id, user_id, schema_id)
            if response.success:
                released_elements.append(element_id)
        
        # Remove o usuário do rastreamento
        del self._user_elements[schema_id][user_id]
        
        logger.info(f"All {len(released_elements)} locks for user {user_id} have been released")
        return released_elements
    
    async def _cleanup_expired_locks(self, schema_id: str) -> None:
        """
        Task que roda continuamente para limpar locks expirados.
        """
        try:
            while True:
                await asyncio.sleep(self.CLEANUP_INTERVAL)
                
                if schema_id not in self._locks:
                    break
                
                element_locks = self._locks[schema_id]
                expired_elements = [
                    (element_id, lock)
                    for element_id, lock in element_locks.items()
                    if lock.is_expired()
                ]
                
                for element_id, lock in expired_elements:
                    await self.release_lock(element_id, lock.user_id, schema_id)
                    logger.info(f"Expired lock automatically removed: {element_id}")
                    
        except asyncio.CancelledError:
            logger.info(f"Lock cleanup cancelled for schema {schema_id}")
    
    async def cleanup_schema(self, schema_id: str) -> None:
        """
        Limpa todos os dados de um schema quando ele é fechado.
        """
        if schema_id in self._locks:
            del self._locks[schema_id]
        
        if schema_id in self._user_elements:
            del self._user_elements[schema_id]
        
        if schema_id in self._cleanup_tasks:
            task = self._cleanup_tasks[schema_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self._cleanup_tasks[schema_id]
        
        logger.info(f"Schema {schema_id} cleaned up from lock manager")
