from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import json
import os
import tempfile
import uuid
import logging

from app.database.common.supabase_client import get_supabase_client
from app.database.common.supabase_public_url import build_public_url
import httpx
from supabase import create_client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/generate-sql",
    tags=["sql"],
)


class GenerateSqlRequest(BaseModel):
    schema: str
    sgbd: str


def _build_groq_prompt(base_prompt: str, schema: str, sgbd: str) -> str:
    schema_str = schema if isinstance(schema, str) else str(schema)
    return f"{base_prompt.strip()}\n\n[SCHEMA_JSON]:\n{schema_str}\n\n[SGBD]: {sgbd.strip()}"


@router.post("")
async def generate_sql(payload: GenerateSqlRequest):
    try:
        from groq import Groq  # imported lazily in case not installed in some envs

        groq_api_key = os.getenv("GROQ_API_KEY")
        base_prompt = """
        Você é um assistente especializado em modelagem de banco de dados. 
        Sua tarefa é gerar um script SQL válido a partir de um esquema de tabelas fornecido em formato JSON. 
        Respeite sempre o SGBD especificado (ex: PostgreSQL, MySQL, Oracle). 
        O resultado deve ser devolvido em JSON estruturado no seguinte formato:
        {
          "sql_code": "CREATE TABLE ..."
        }
        Certifique-se de:
        1. Definir corretamente chaves primárias e estrangeiras.
        2. Usar os tipos de dados compatíveis com o SGBD informado.
        3. Incluir constraints (NOT NULL, UNIQUE, DEFAULT) quando fizer sentido.
        4. Gerar o SQL pronto para execução direta no banco.
        """

        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY não configurada")

        prompt = _build_groq_prompt(base_prompt, payload.schema, payload.sgbd)

        # Provide explicit httpx.Client to avoid SDK constructing one with unsupported 'proxies' kwarg
        http_client = httpx.Client()
        client = Groq(api_key=groq_api_key, http_client=http_client)

        completion = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            messages=[
                {"role": "system", "content": "Você é um assistente que responde apenas em JSON válido."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        content = completion.choices[0].message.content if completion and completion.choices else None
        try:
            parsed: Dict[str, Any] = json.loads(content) if content else {}
        except Exception:
            parsed = {}

        sql_code = parsed.get("sql_code") if isinstance(parsed, dict) else None
        if not sql_code or not isinstance(sql_code, str) or not sql_code.strip():
            raise HTTPException(status_code=502, detail="Groq não retornou sql_code válido")

        tmp_filename = f"{uuid.uuid4()}.sql"
        tmp_path = os.path.join(tempfile.gettempdir(), tmp_filename)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(sql_code)

        # Use bucket-specific key for storage operations (private bucket / RLS)
        connection_url = (os.getenv("CONNECTION_POSTGRES_SUPABASE") or "").strip()
        bucket_key = (os.getenv("SECRET_SUPABASE_BUCKET") or "").strip()
        if not connection_url or not bucket_key:
            raise HTTPException(status_code=500, detail="CONNECTION_POSTGRES_SUPABASE/SECRET_SUPABASE_BUCKET não configurados")
        supabase = create_client(connection_url, bucket_key)
        with open(tmp_path, "rb") as f:
            file_bytes = f.read()

        bucket_name = "exports"
        file_path = tmp_filename

        storage_bucket = supabase.storage.from_(bucket_name)
        upload_resp = storage_bucket.upload(
            path=file_path,
            file=file_bytes,
            file_options={
                "content-type": "application/sql",
                "upsert": "true",
            },
        )

        if hasattr(upload_resp, "error") and upload_resp.error:
            raise HTTPException(status_code=500, detail=f"Erro no upload do SQL: {upload_resp.error}")
        if isinstance(upload_resp, dict) and upload_resp.get("error"):
            raise HTTPException(status_code=500, detail=f"Erro no upload do SQL: {upload_resp['error']}")

        # Generate signed URL for private bucket
        try:
            signed = storage_bucket.create_signed_url(path=file_path, expires_in=3600)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao gerar signed URL: {str(e)}")

        if hasattr(signed, "error") and signed.error:
            raise HTTPException(status_code=500, detail=f"Erro ao gerar signed URL: {signed.error}")
        if isinstance(signed, dict) and signed.get("error"):
            raise HTTPException(status_code=500, detail=f"Erro ao gerar signed URL: {signed['error']}")

        signed_url = None
        if isinstance(signed, dict):
            signed_url = signed.get("signedURL") or signed.get("signed_url") or signed.get("url")
        if not signed_url:
            raise HTTPException(status_code=500, detail="Não foi possível obter signed URL")

        # attempt to force download with explicit filename to keep .sql extension
        download_name = file_path
        if "?" in signed_url:
            signed_url = f"{signed_url}&download={download_name}"
        else:
            signed_url = f"{signed_url}?download={download_name}"

        # cleanup temp file
        try:
            os.remove(tmp_path)
        except Exception:
            pass

        return {"url": signed_url}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro ao gerar SQL")
        raise HTTPException(status_code=500, detail=str(e))


