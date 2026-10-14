"""Configurações centrais. Mude aqui para experimentar."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*_args, **_kwargs):
        return False


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=False)


def _obter_bool(chave: str, padrao: bool) -> bool:
    valor = os.getenv(chave)
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "yes", "on"}


# Provedor de LLM: anthropic ou openrouter.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").strip().lower()

# OpenRouter (opcional). Quando configurado, isto passa a ser o provedor ativo
# por padrão, desde que a chave exista.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "https://localhost")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "orquestraca-agentes")
OPENROUTER_MAX_TOKENS = int(os.getenv("OPENROUTER_MAX_TOKENS", "2048"))

# Jev faz decisões tipadas; OpenRouter continua responsável pela geração de texto.
TYPESAFE_API_KEY = os.getenv("TYPESAFE_API_KEY", "").strip()
TYPESAFE_MODEL = os.getenv("TYPESAFE_MODEL", "jev-latest")
USAR_JEV_ROTEAMENTO = _obter_bool("USAR_JEV_ROTEAMENTO", True)

# Modelo usado por todos os agentes. Se o provedor for OpenRouter, prefira
# OPENROUTER_MODEL; do contrário, usa ANTHROPIC_MODEL.
ANTHROPIC_MODEL_PADRAO = "claude-opus-5-5"
OPENROUTER_MODEL_PADRAO = "nvidia/nemotron-3-ultra-550b-a55b"

if OPENROUTER_API_KEY and not LLM_PROVIDER:
    LLM_PROVIDER = "openrouter"
elif not LLM_PROVIDER:
    LLM_PROVIDER = "anthropic"

MODELO = (
    os.getenv("OPENROUTER_MODEL")
    or os.getenv("ANTHROPIC_MODEL")
    or (OPENROUTER_MODEL_PADRAO if LLM_PROVIDER == "openrouter" else ANTHROPIC_MODEL_PADRAO)
)

# Chaves da API lidas a partir do ambiente ou do arquivo .env.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()

# Quanto o modelo "pensa" antes de responder: low, medium, high, xhigh, max.
# Mais esforço = respostas melhores em tarefas difíceis, porém mais lento e caro.
EFFORT_PADRAO = os.getenv("EFFORT_PADRAO", "medium")
EFFORT_TRABALHADOR = os.getenv("EFFORT_TRABALHADOR", "low")

# Trava de segurança: número máximo de idas e voltas no loop de cada agente.
MAX_PASSOS = int(os.getenv("MAX_PASSOS", "10"))

# Orçamento acumulado de tokens de entrada + saída por execução de agente.
TOKEN_BUDGET = int(os.getenv("TOKEN_BUDGET", "20000"))

# Recursos de acompanhamento.
ATIVAR_METRICAS = _obter_bool("ATIVAR_METRICAS", True)
MAX_TRABALHOS_PARARELOS = int(os.getenv("MAX_TRABALHOS_PARARELOS", "8"))


def validar_configuracao() -> None:
    """Levanta uma mensagem clara quando a chave da API não está disponível."""
    if LLM_PROVIDER == "openrouter":
        if not OPENROUTER_API_KEY:
            raise RuntimeError(
                "OPENROUTER_API_KEY não definida. Configure a variável de ambiente "
                "ou crie um arquivo .env na raiz do projeto com OPENROUTER_API_KEY=..."
            )
        return

    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY não definida. Configure a variável de ambiente "
            "ou crie um arquivo .env na raiz do projeto com ANTHROPIC_API_KEY=..."
        )
