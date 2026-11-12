import secrets

from fastapi import Header, HTTPException

from maintai.config import get_settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    settings = get_settings()

    # Si le serveur n'a pas de clé configurée, on lève une erreur 500
    if not settings.api_key:
        raise HTTPException(
            status_code=500, detail="Clé API non configurée sur le serveur"
        )

    # Si la clé est absente ou ne correspond pas, on refuse avec un code 401[cite: 7, 20]
    if x_api_key is None or not secrets.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(status_code=401, detail="Clé API absente ou invalide")

    return x_api_key
