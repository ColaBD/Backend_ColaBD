from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -> str = significa que retorna uma string
def gerar_hash_senha(password: str) -> str:
  return pwd_context.hash(password)

def verificar_hash_senha(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)
