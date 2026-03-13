"""
Gerenciamento de sessão persistente via cookies do navegador.
Os dados do usuário são assinados com HMAC para evitar adulteração.
"""

import json
import hmac
import hashlib
import base64
import os
from typing import Optional

import streamlit as st

SECRET_KEY = os.environ.get("SESSION_SECRET", "isp-manager-secret-key-change-in-production")
COOKIE_NAME = "isp_session"
COOKIE_MAX_AGE = 30 * 24 * 3600  # 30 dias


# ── Sessões revogadas (memória do processo) ──────────────────────────────────
# Persiste enquanto o servidor Streamlit estiver rodando — sobrevive a F5/rerun.
# User IDs aqui não terão a sessão restaurada via cookie mesmo que o cookie
# ainda esteja no browser (deleção de cookie é assíncrona no CookieManager).

_revoked_user_ids: set = set()


def revoke_session(user_id) -> None:
    """Marca o user_id como deslogado no servidor."""
    if user_id is not None:
        _revoked_user_ids.add(str(user_id))


def unrevoke_session(user_id) -> None:
    """Remove a revogação ao fazer login novamente."""
    _revoked_user_ids.discard(str(user_id))


def _is_revoked(user_id) -> bool:
    return str(user_id) in _revoked_user_ids


# ── Codificação / decodificação segura ───────────────────────────────────────

def _sign(data: str) -> str:
    return hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()


def _encode_session(user_data: dict) -> str:
    payload = {
        "user_id":      user_data.get("id") or user_data.get("user_id"),
        "company_id":   user_data["company_id"],
        "company_name": user_data["company_name"],
        "username":     user_data["username"],
        "full_name":    user_data["full_name"],
        "team":         user_data["team"],
        "role":         user_data["role"],
        "is_super_admin": user_data.get("is_super_admin", False),
    }
    data_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    return f"{data_b64}.{_sign(data_b64)}"


def _decode_session(value: str) -> Optional[dict]:
    try:
        data_b64, sig = value.rsplit(".", 1)
        if not hmac.compare_digest(sig, _sign(data_b64)):
            return None
        return json.loads(base64.b64decode(data_b64).decode())
    except Exception:
        return None


# ── Gerenciador de cookies ───────────────────────────────────────────────────

def init_cookie_manager():
    """
    Cria e armazena o CookieManager no session_state.
    Deve ser chamado UMA VEZ no início de main(), antes de qualquer UI condicional.
    Retorna a instância ou None se a biblioteca não estiver disponível.
    """
    try:
        import extra_streamlit_components as stx
        cm = stx.CookieManager(key="isp_cm")
        st.session_state["_cm"] = cm
        return cm
    except ImportError:
        st.session_state["_cm"] = None
        return None


def _get_cm():
    return st.session_state.get("_cm")


# ── API pública ───────────────────────────────────────────────────────────────

def set_session_cookie(user_data: dict) -> None:
    """Salva dados do usuário em cookie persistente assinado."""
    cm = _get_cm()
    if cm is None:
        return
    try:
        cm.set(COOKIE_NAME, _encode_session(user_data), max_age=COOKIE_MAX_AGE)
    except Exception:
        pass


def clear_session_cookie() -> None:
    """Remove o cookie de sessão do navegador."""
    cm = _get_cm()
    if cm is None:
        return
    try:
        cm.delete(COOKIE_NAME)
    except Exception:
        pass


def get_session_from_cookie() -> Optional[dict]:
    """
    Lê e verifica o cookie de sessão.
    Retorna dict com dados do usuário ou None se inexistente/inválido/revogado.
    """
    cm = _get_cm()
    if cm is None:
        return None
    try:
        value = cm.get(COOKIE_NAME)
        if not value:
            return None
        data = _decode_session(value)
        if data is None:
            return None
        # Bloqueia restauração se o usuário fez logout explícito neste processo
        if _is_revoked(data.get("user_id")):
            return None
        return data
    except Exception:
        return None
