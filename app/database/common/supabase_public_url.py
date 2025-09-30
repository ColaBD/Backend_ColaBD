import os


def build_public_url(bucket_name: str, file_path: str) -> str:
    connection_url = (os.getenv('CONNECTION_POSTGRES_SUPABASE') or '').strip()
    if not connection_url:
        raise RuntimeError('CONNECTION_POSTGRES_SUPABASE não configurada')
    base = connection_url.rstrip('/')
    return f"{base}/storage/v1/object/public/{bucket_name}/{file_path}"


