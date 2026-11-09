import html
import os
import uuid
import streamlit as st
import requests

# 1. CONFIGURAÇÃO DA PÁGINA (Aba do browser)
st.set_page_config(
    page_title="Zélia • Playground Acadêmico",
    page_icon="⭕",
    layout="centered",
    initial_sidebar_state="collapsed"
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/perguntar")

# Inicializa estados da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []
if "student_name" not in st.session_state:
    st.session_state.student_name = "Fábio"
if "student_course" not in st.session_state:
    st.session_state.student_course = "Engenharia de Software"
if "student_registration" not in st.session_state:
    st.session_state.student_registration = "20261001"
if "preview_thinking" not in st.session_state:
    st.session_state.preview_thinking = False


def get_zelia_logo_svg(thinking: bool = False, size: int = 44) -> str:
    """Retorna o SVG da logo da Zélia (4 círculos concêntricos).
    - Estado normal: tons de vermelho concêntricos.
    - Estado pensando: gradiente dinâmico animado variando entre vermelho e azul.
    """
    uid = uuid.uuid4().hex[:6]
    state_class = "zelia-logo-thinking" if thinking else "zelia-logo-idle"
    stroke_1 = f"url(#zeliaGradThink1_{uid})" if thinking else "#ef4444"
    stroke_2 = f"url(#zeliaGradThink2_{uid})" if thinking else "#dc2626"
    stroke_3 = f"url(#zeliaGradThink1_{uid})" if thinking else "#b91c1c"
    fill_4 = f"url(#zeliaGradThink2_{uid})" if thinking else f"url(#zeliaGradRed_{uid})"
    return (
        f'<span class="zelia-logo-wrapper {state_class}" style="width:{size}px;height:{size}px;" '
        f'title="{"Zélia está pensando..." if thinking else "Zélia - Assistente Virtual"}">'
        f'<svg viewBox="0 0 100 100" width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>'
        f'<linearGradient id="zeliaGradRed_{uid}" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="#ff4d4d" />'
        f'<stop offset="100%" stop-color="#b91c1c" />'
        f'</linearGradient>'
        f'<linearGradient id="zeliaGradThink1_{uid}" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="#ef4444">'
        f'<animate attributeName="stop-color" values="#ef4444;#3b82f6;#8b5cf6;#ef4444" dur="2.2s" repeatCount="indefinite" />'
        f'</stop>'
        f'<stop offset="100%" stop-color="#2563eb">'
        f'<animate attributeName="stop-color" values="#2563eb;#ef4444;#06b6d4;#2563eb" dur="2.2s" repeatCount="indefinite" />'
        f'</stop>'
        f'</linearGradient>'
        f'<linearGradient id="zeliaGradThink2_{uid}" x1="100%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" stop-color="#3b82f6">'
        f'<animate attributeName="stop-color" values="#3b82f6;#ef4444;#ec4899;#3b82f6" dur="2.2s" repeatCount="indefinite" />'
        f'</stop>'
        f'<stop offset="100%" stop-color="#dc2626">'
        f'<animate attributeName="stop-color" values="#dc2626;#1d4ed8;#ef4444;#dc2626" dur="2.2s" repeatCount="indefinite" />'
        f'</stop>'
        f'</linearGradient>'
        f'</defs>'
        # Círculo 1 (Externo)
        f'<circle class="ring ring-1" cx="50" cy="50" r="44" fill="none" stroke="{stroke_1}" stroke-width="5.5" />'
        # Círculo 2 (Médio-Externo)
        f'<circle class="ring ring-2" cx="50" cy="50" r="32" fill="none" stroke="{stroke_2}" stroke-width="5.5" />'
        # Círculo 3 (Médio-Interno)
        f'<circle class="ring ring-3" cx="50" cy="50" r="20" fill="none" stroke="{stroke_3}" stroke-width="5.5" />'
        # Círculo 4 (Núcleo Concêntrico)
        f'<circle class="ring ring-4" cx="50" cy="50" r="8.5" fill="{fill_4}" />'
        f'</svg>'
        f'</span>'
    )


# 2. ESTILIZAÇÃO VISUAL (Inspirada no Microsoft AI Playground)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Fundo suave estilo Microsoft AI Playground */
    .stApp {
        background: radial-gradient(circle at 50% 0%, rgba(239, 68, 68, 0.06) 0%, rgba(59, 130, 246, 0.04) 45%, transparent 75%);
    }

    /* Ajuste de espaçamento central */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 6rem !important;
        max-width: 780px !important;
    }

    /* Cabeçalho / Hero acima do chat */
    .zelia-hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin: 1.5rem 0 2rem 0;
        padding: 1.5rem 1.25rem;
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(148, 163, 184, 0.14);
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 35px -10px rgba(0, 0, 0, 0.08);
        transition: all 0.35s ease;
    }

    .zelia-hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 0.9rem;
        color: #ef4444;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.22);
    }

    .zelia-hero-badge.thinking {
        color: #60a5fa;
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.15), rgba(59, 130, 246, 0.18));
        border: 1px solid rgba(96, 165, 250, 0.35);
    }

    .zelia-greeting-row {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex-wrap: wrap;
        gap: 14px;
        font-size: clamp(1.45rem, 3vw, 2.05rem);
        font-weight: 700;
        line-height: 1.25;
        letter-spacing: -0.02em;
    }

    .zelia-greeting-subtitle {
        margin-top: 0.55rem;
        font-size: 0.94rem;
        opacity: 0.72;
        max-width: 540px;
    }

    /* =====================================================
       LOGO DA ZÉLIA: 4 CÍRCULOS CONCÊNTRICOS
       ===================================================== */
    .zelia-logo-wrapper {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        vertical-align: middle;
        position: relative;
        flex-shrink: 0;
    }

    /* Estado Ocioso (Idle): 4 círculos concêntricos vermelhos */
    .zelia-logo-idle .ring-1 {
        opacity: 0.38;
        transform-origin: 50% 50%;
        animation: zeliaIdleBreathe 4s ease-in-out infinite;
    }
    .zelia-logo-idle .ring-2 {
        opacity: 0.60;
        transform-origin: 50% 50%;
        animation: zeliaIdleBreathe 4s ease-in-out infinite 0.3s;
    }
    .zelia-logo-idle .ring-3 {
        opacity: 0.85;
        transform-origin: 50% 50%;
        animation: zeliaIdleBreathe 4s ease-in-out infinite 0.6s;
    }
    .zelia-logo-idle .ring-4 {
        transform-origin: 50% 50%;
        animation: zeliaIdleBreathe 4s ease-in-out infinite 0.9s;
    }

    /* Estado Pensando (Thinking): Gradiente dinâmico entre Vermelho e Azul */
    .zelia-logo-thinking {
        filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.45)) drop-shadow(0 0 14px rgba(239, 68, 68, 0.35));
    }
    .zelia-logo-thinking .ring-1 {
        stroke-dasharray: 210 70;
        transform-origin: 50% 50%;
        animation: zeliaSpinCW 2.2s linear infinite, zeliaPulseRing 1.6s ease-in-out infinite;
    }
    .zelia-logo-thinking .ring-2 {
        stroke-dasharray: 150 50;
        transform-origin: 50% 50%;
        animation: zeliaSpinCCW 1.8s linear infinite, zeliaPulseRing 1.6s ease-in-out infinite 0.2s;
    }
    .zelia-logo-thinking .ring-3 {
        stroke-dasharray: 95 30;
        transform-origin: 50% 50%;
        animation: zeliaSpinCW 1.4s linear infinite, zeliaPulseRing 1.6s ease-in-out infinite 0.4s;
    }
    .zelia-logo-thinking .ring-4 {
        transform-origin: 50% 50%;
        animation: zeliaCorePulse 1.1s ease-in-out infinite alternate;
    }

    @keyframes zeliaIdleBreathe {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.04); }
    }

    @keyframes zeliaSpinCW {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes zeliaSpinCCW {
        0% { transform: rotate(360deg); }
        100% { transform: rotate(0deg); }
    }

    @keyframes zeliaPulseRing {
        0%, 100% { opacity: 0.95; }
        50% { opacity: 0.55; }
    }

    @keyframes zeliaCorePulse {
        0% { transform: scale(0.85); }
        100% { transform: scale(1.22); }
    }

    /* Card de status quando está pensando dentro do chat */
    .zelia-thinking-inline {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        padding: 8px 16px;
        border-radius: 999px;
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.10), rgba(59, 130, 246, 0.12));
        border: 1px solid rgba(99, 102, 241, 0.25);
        font-size: 0.92rem;
        font-weight: 500;
    }

    /* Estilização do campo de chat estilo Playground */
    [data-testid="stChatInput"] {
        border-radius: 999px !important;
    }

    [data-testid="stChatMessage"] {
        border-radius: 18px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.65rem;
        border: 1px solid rgba(148, 163, 184, 0.12);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_hero(placeholder, student_name: str, student_course: str = "", thinking: bool = False):
    """Renderiza a frase principal acima do chat com o nome do aluno e a logo da Zélia ao final."""
    nome_exibicao = html.escape(student_name.strip() or "Estudante")
    curso_exibicao = html.escape(student_course.strip())
    logo_html = get_zelia_logo_svg(thinking=thinking, size=46)
    badge_class = "zelia-hero-badge thinking" if thinking else "zelia-hero-badge"
    if thinking:
        badge_text = "Processando resposta • IA Unijorge"
    elif curso_exibicao:
        badge_text = f"Zélia • {curso_exibicao}"
    else:
        badge_text = "Zélia • Assistente Universitária"

    subtitulo = (
        "Consultando os documentos oficiais e o Manual do Aluno em tempo real..."
        if thinking
        else "Tire dúvidas sobre o Manual do Aluno, calendários, matrículas, prazos e normas acadêmicas."
    )

    placeholder.markdown(
        f"""
        <div class="zelia-hero-container">
            <div class="{badge_class}">{badge_text}</div>
            <div class="zelia-greeting-row">
                <span>O que vamos conversar hoje, {nome_exibicao}?</span>
                {logo_html}
            </div>
            <div class="zelia-greeting-subtitle">{subtitulo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# 3. BARRA LATERAL (Configurações do Aluno, Integração Lyceum e Controles)
with st.sidebar:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">'
        f'{get_zelia_logo_svg(thinking=st.session_state.preview_thinking, size=38)}'
        f'<div><strong style="font-size:1.1rem;">Zélia AI</strong><br>'
        f'<span style="font-size:0.8rem;opacity:0.7;">Unijorge • Contexto Lyceum</span></div></div>',
        unsafe_allow_html=True,
    )

    st.session_state.student_name = st.text_input(
        "👤 Nome do aluno logado",
        value=st.session_state.student_name,
        help="Altera o nome exibido na saudação principal acima do chat."
    )

    cursos_disponiveis = [
        "Engenharia de Software",
        "Ciência da Computação",
        "Sistemas de Informação",
        "Direito",
        "Administração",
        "Psicologia",
        "Enfermagem",
        "Arquitetura e Urbanismo",
        "Outro / Geral",
    ]
    indice_curso = (
        cursos_disponiveis.index(st.session_state.student_course)
        if st.session_state.student_course in cursos_disponiveis
        else 0
    )
    st.session_state.student_course = st.selectbox(
        "🎓 Curso (Contexto Lyceum)",
        options=cursos_disponiveis,
        index=indice_curso,
        help="Contextualiza as respostas da Zélia conforme o curso de matrícula do estudante."
    )

    st.session_state.student_registration = st.text_input(
        "🪪 Matrícula",
        value=st.session_state.student_registration,
        help="Identificador acadêmico para consulta contextual no conector Lyceum."
    )

    st.session_state.preview_thinking = st.toggle(
        "✨ Simular estado 'Pensando'",
        value=st.session_state.preview_thinking,
        help="Ative para visualizar a animação gradiente vermelho/azul da logo da Zélia."
    )

    st.divider()
    st.info(
        "Olá! Sou a **Zélia**, assistente virtual da Unijorge para dúvidas sobre o "
        "**Manual do Aluno**, calendários e processos acadêmicos."
    )

    if st.button("🗑️ Nova Conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# 4. CABEÇALHO DINÂMICO ACIMA DO CHAT
hero_placeholder = st.empty()
render_hero(
    hero_placeholder,
    student_name=st.session_state.student_name,
    student_course=st.session_state.student_course,
    thinking=st.session_state.preview_thinking,
)

# Sugestões rápidas estilo Playground quando a conversa está vazia
prompt_sugerido = None
if not st.session_state.messages:
    cols = st.columns(3)
    sugestoes = [
        "📅 Qual o prazo para trancamento?",
        "📚 Como funciona o limite de faltas?",
        "🎓 Como solicitar segunda chamada?",
    ]
    for col, sugestao in zip(cols, sugestoes):
        if col.button(sugestao, use_container_width=True):
            prompt_sugerido = sugestao

# 5. EXIBIR HISTÓRICO DE MENSAGENS
for message in st.session_state.messages:
    avatar_icon = "🧑‍🎓" if message["role"] == "user" else "⭕"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# 6. ENTRADA DO CHAT E RESPOSTA COM ANIMAÇÃO DE PENSAMENTO
prompt_digitado = st.chat_input(f"Pergunte qualquer coisa para a Zélia, {st.session_state.student_name}...")
prompt = prompt_digitado or prompt_sugerido

if prompt:
    # Guarda o histórico anterior (sem duplicar a pergunta atual)
    historico_anterior = list(st.session_state.messages[-8:])

    # Adiciona e exibe a pergunta do aluno
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    # Atualiza a logo do topo para o modo "Pensando" (gradiente vermelho <-> azul)
    render_hero(
        hero_placeholder,
        student_name=st.session_state.student_name,
        student_course=st.session_state.student_course,
        thinking=True,
    )

    # Exibe a resposta da Zélia com indicador animado vermelho-azul enquanto aguarda a API
    with st.chat_message("assistant", avatar="⭕"):
        message_placeholder = st.empty()
        message_placeholder.markdown(
            f'<div class="zelia-thinking-inline">'
            f'{get_zelia_logo_svg(thinking=True, size=28)}'
            f'<span>Zélia está consultando os documentos e pensando...</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        try:
            payload = {
                "query": prompt,
                "history": historico_anterior,
                "student_name": st.session_state.student_name,
                "student_course": st.session_state.student_course,
                "student_registration": st.session_state.student_registration,
            }

            response = requests.post(API_URL, json=payload, timeout=60)

            if response.status_code == 200:
                dados_resp = response.json()
                resposta_ia = dados_resp.get("answer", "Desculpe, não consegui obter a resposta.")
                message_placeholder.markdown(resposta_ia)
                st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
            else:
                message_placeholder.markdown(f"❌ Erro na API: Status {response.status_code}")

        except requests.exceptions.Timeout:
            message_placeholder.markdown("❌ O servidor demorou muito para responder (Timeout). Tente novamente!")
        except requests.exceptions.ConnectionError:
            message_placeholder.markdown("❌ Erro de ligação ao servidor FastAPI! Verifique se o backend está rodando.")
        except requests.exceptions.RequestException:
            message_placeholder.markdown("❌ Ocorreu um erro inesperado ao comunicar com o servidor!")
        finally:
            # Retorna a logo do topo para o estado normal (4 círculos vermelhos) após responder
            render_hero(
                hero_placeholder,
                student_name=st.session_state.student_name,
                student_course=st.session_state.student_course,
                thinking=st.session_state.preview_thinking,
            )
