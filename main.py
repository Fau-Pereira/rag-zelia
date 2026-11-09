import logging
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict, List, Literal, Optional
from rag_core import get_rag_response
from lyceum_client import obter_contexto_estudante

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(
    title="API Zélia - Assistente Acadêmica",
    description="API de atendimento acadêmico inteligente baseada em RAG e Agentes LangGraph (Unijorge).",
    version="1.1.0",
)

# Métricas em memória para observabilidade e monitoramento
METRICAS_EXECUCAO: Dict[str, Any] = {
    "total_requisicoes": 0,
    "total_sucesso": 0,
    "total_erros": 0,
    "soma_latencia_ms": 0.0,
}


# Estrutura para receber o histórico de mensagens (restrito aos papéis válidos)
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


# Atualizamos a requisição para receber a pergunta, o histórico e o contexto acadêmico opcional (Lyceum)
class QuestionRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    history: Optional[List[Message]] = Field(default_factory=list, max_length=20)
    student_name: Optional[str] = Field(default=None, max_length=120)
    student_course: Optional[str] = Field(default=None, max_length=120)
    student_registration: Optional[str] = Field(default=None, max_length=40)

    @field_validator("query")
    @classmethod
    def query_nao_vazia(cls, v: str) -> str:
        texto = v.strip()
        if not texto:
            raise ValueError("A pergunta não pode estar vazia.")
        return texto


@app.get("/health")
def health_check():
    """Endpoint de verificação de saúde e disponibilidade da API."""
    return {"status": "ok", "service": "Zélia API"}


@app.get("/metrics")
def obter_metricas():
    """Endpoint de observabilidade com contagem de chamadas e latência média."""
    total_sucesso = METRICAS_EXECUCAO["total_sucesso"]
    latencia_media = (
        round(METRICAS_EXECUCAO["soma_latencia_ms"] / total_sucesso, 2)
        if total_sucesso > 0
        else 0.0
    )
    return {
        "total_requests": METRICAS_EXECUCAO["total_requisicoes"],
        "successful_requests": total_sucesso,
        "failed_requests": METRICAS_EXECUCAO["total_erros"],
        "avg_latency_ms": latencia_media,
    }


@app.post("/perguntar")
def perguntar_ao_manual(request: QuestionRequest):
    inicio = time.perf_counter()
    METRICAS_EXECUCAO["total_requisicoes"] += 1

    try:
        historico = request.history or []
        history_dict = [{"role": msg.role, "content": msg.content} for msg in historico]

        # Constrói o contexto acadêmico do estudante (Integração Lyceum)
        student_context = None
        if request.student_name or request.student_course or request.student_registration:
            identificador = request.student_registration or request.student_name or ""
            perfil = obter_contexto_estudante(
                identificador=identificador,
                curso_informado=request.student_course or "",
            )
            student_context = {
                "student_name": request.student_name or (perfil.get("nome") if perfil else "Estudante"),
                "student_course": request.student_course or (perfil.get("curso") if perfil else "Não informado"),
                "student_registration": request.student_registration or (perfil.get("matricula") if perfil else "Não informada"),
            }

        try:
            answer = get_rag_response(request.query, history_dict, student_context=student_context)
        except TypeError:
            # Mantém compatibilidade caso get_rag_response seja mockado com apenas 2 argumentos em testes
            answer = get_rag_response(request.query, history_dict)

        latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)
        METRICAS_EXECUCAO["total_sucesso"] += 1
        METRICAS_EXECUCAO["soma_latencia_ms"] += latencia_ms
        logging.info(f"Pergunta processada com sucesso em {latencia_ms} ms.")

        return {"answer": answer, "latency_ms": latencia_ms}

    except Exception:
        METRICAS_EXECUCAO["total_erros"] += 1
        logging.exception("Erro interno ao processar a pergunta na API Zélia.")
        raise HTTPException(
            status_code=500,
            detail="Ocorreu um erro interno ao processar a sua solicitação. Tente novamente em instantes.",
        )
