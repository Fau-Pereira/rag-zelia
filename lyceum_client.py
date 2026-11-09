"""Módulo de integração com o sistema acadêmico Lyceum (MVP / Simulador + Conector HTTP).

Permite recuperar o contexto acadêmico do estudante (curso, campus, semestre e situação)
para personalizar o atendimento da Zélia sem expor dados sensíveis indevidamente.
"""

import logging
import os
from typing import Any, Dict, Optional
import requests

LYCEUM_API_URL = os.getenv("LYCEUM_API_URL", "").strip()
LYCEUM_API_TOKEN = os.getenv("LYCEUM_API_TOKEN", "").strip()

# Perfis acadêmicos demonstrativos para validação do MVP (dados fictícios/institucionais)
PERFIS_DEMO_LYCEUM: Dict[str, Dict[str, Any]] = {
    "fabio": {
        "nome": "Fábio Pereira",
        "matricula": "20261001",
        "curso": "Engenharia de Software",
        "modalidade": "Presencial",
        "campus": "Paralela",
        "semestre": "5º Semestre",
        "situacao": "Matrícula Ativa",
        "coordenacao": "Coordenação de Computação e Engenharias",
    },
    "20261001": {
        "nome": "Fábio Pereira",
        "matricula": "20261001",
        "curso": "Engenharia de Software",
        "modalidade": "Presencial",
        "campus": "Paralela",
        "semestre": "5º Semestre",
        "situacao": "Matrícula Ativa",
        "coordenacao": "Coordenação de Computação e Engenharias",
    },
    "maria": {
        "nome": "Maria Souza",
        "matricula": "20261002",
        "curso": "Direito",
        "modalidade": "Presencial",
        "campus": "Paralela",
        "semestre": "3º Semestre",
        "situacao": "Matrícula Ativa",
        "coordenacao": "Coordenação do Curso de Direito",
    },
    "joao": {
        "nome": "João Santos",
        "matricula": "20261003",
        "curso": "Administração",
        "modalidade": "EAD",
        "campus": "Comércio",
        "semestre": "2º Semestre",
        "situacao": "Matrícula Ativa",
        "coordenacao": "Coordenação de Negócios e Gestão",
    },
}


def obter_contexto_estudante(identificador: str = "", curso_informado: str = "") -> Optional[Dict[str, Any]]:
    """Busca o perfil acadêmico do estudante no conector Lyceum (API real se configurada ou base de demonstração)."""
    chave = identificador.strip().lower()
    if chave in ("fábio", "fabio pereira", "fábio pereira"):
        chave = "fabio"

    # 1. Se houver endpoint institucional configurado, consulta a API do Lyceum com autenticação
    if LYCEUM_API_URL and LYCEUM_API_TOKEN and chave:
        try:
            headers = {"Authorization": f"Bearer {LYCEUM_API_TOKEN}"}
            resp = requests.get(f"{LYCEUM_API_URL.rstrip('/')}/alunos/{chave}", headers=headers, timeout=5)
            if resp.status_code == 200:
                dados = resp.json()
                if isinstance(dados, dict):
                    return dados
        except requests.exceptions.RequestException as exc:
            logging.warning(f"Falha ao consultar API Lyceum ({exc}). Utilizando perfil local.")

    # 2. Fallback para base demonstrativa local
    if chave in PERFIS_DEMO_LYCEUM:
        perfil = dict(PERFIS_DEMO_LYCEUM[chave])
        if curso_informado.strip():
            perfil["curso"] = curso_informado.strip()
        return perfil

    # 3. Se o estudante informou nome ou curso na sessão, constrói o contexto dinâmico
    if identificador.strip() or curso_informado.strip():
        return {
            "nome": identificador.strip() or "Estudante",
            "matricula": "Não informada",
            "curso": curso_informado.strip() or "Curso Geral (Graduação)",
            "modalidade": "Presencial / EAD",
            "campus": "Unijorge - Salvador",
            "semestre": "Em curso",
            "situacao": "Ativo",
            "coordenacao": "Atendimento Acadêmico Unijorge",
        }

    return None
