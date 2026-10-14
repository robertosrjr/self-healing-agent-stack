"""
O bloco básico de tudo: um Agente.

Um agente é só isto:
    1. um modelo de linguagem (OpenRouter ou Anthropic)
    2. um "system prompt" que define o papel dele
    3. um conjunto de ferramentas que ele pode chamar
    4. um LOOP: chama o modelo -> se ele pediu ferramentas, executa e devolve
       o resultado -> chama de novo -> ... até ele dar a resposta final.

O orquestrador também é um Agente. A diferença é que uma das ferramentas dele
é "delegar para outro agente".
"""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import time
from types import SimpleNamespace
from typing import Callable

import anthropic
from openai import OpenAI

import config

def _criar_cliente():
    """Cria o cliente do provedor selecionado."""
    config.validar_configuracao()
    if config.LLM_PROVIDER == "openrouter":
        base_url = config.OPENROUTER_BASE_URL.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        return OpenAI(
            api_key=config.OPENROUTER_API_KEY,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": config.OPENROUTER_SITE_URL,
                "X-OpenRouter-Title": config.OPENROUTER_APP_NAME,
            },
        )
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


# Um cliente só, reaproveitado por todos os agentes.
client = _criar_cliente()


@dataclass
class Ferramenta:
    """Uma ferramenta = descrição para o modelo + função Python que a executa."""

    nome: str
    descricao: str
    parametros: dict  # JSON Schema dos argumentos
    funcao: Callable[..., str]

    def definicao_para_api(self) -> dict:
        return {
            "name": self.nome,
            "description": self.descricao,
            "input_schema": self.parametros,
        }


@dataclass
class Agente:
    nome: str
    system: str
    ferramentas: list[Ferramenta] = field(default_factory=list)
    effort: str = config.EFFORT_PADRAO
    nivel: int = 0  # só para indentar os logs (0 = orquestrador, 1 = trabalhador)
    ultima_execucao: dict = field(default_factory=dict)
    sessao_id: str | None = None

    # ------------------------------------------------------------------ logs
    def _log(self, msg: str) -> None:
        prefixo = "    " * self.nivel
        print(f"{prefixo}[{self.nome}] {msg}")

    def _log_metricas(self, metrica: dict) -> None:
        if not config.ATIVAR_METRICAS:
            return
        self._log(
            "métricas: "
            f"passos={metrica.get('passos')}, "
            f"input={metrica.get('input_tokens', 0)}, "
            f"output={metrica.get('output_tokens', 0)}, "
            f"tempo={metrica.get('tempo_segundos', 0):.2f}s"
        )

    # ------------------------------------------------------------- execução
    def executar(self, tarefa: str) -> str:
        """Roda o loop do agente até ele terminar e devolve o texto final."""
        if config.MAX_PASSOS < 1:
            raise ValueError("MAX_PASSOS deve ser maior que zero.")
        if config.TOKEN_BUDGET < 1:
            raise ValueError("TOKEN_BUDGET deve ser maior que zero.")

        self._log(f"recebeu tarefa: {_resumo(tarefa)}")
        inicio = time.monotonic()
        if self.sessao_id:
            criar_sessao(self.sessao_id, tarefa, status="em_execucao")
            registrar_etapa_execucao(self.sessao_id, f"{self.nome}.inicio", "executando", {"tarefa": tarefa, "nivel": self.nivel})

        mapa_ferramentas = {f.nome: f for f in self.ferramentas}
        if config.LLM_PROVIDER == "openrouter":
            mensagens: list = [
                {"role": "system", "content": self.system},
                {"role": "user", "content": tarefa},
            ]
        else:
            mensagens = [{"role": "user", "content": tarefa}]
        total_input_tokens = 0
        total_output_tokens = 0

        for passo in range(1, config.MAX_PASSOS + 1):
            if self.sessao_id:
                registrar_etapa_execucao(self.sessao_id, f"{self.nome}.passo_{passo}", "executando", {"passo": passo})

            try:
                resposta = self._chamar_modelo(mensagens)
            except Exception as exc:
                self._log(f"erro ao chamar o modelo: {type(exc).__name__}: {exc}")
                self.ultima_execucao = {
                    "passos": passo,
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "tokens_total": total_input_tokens + total_output_tokens,
                    "token_budget": config.TOKEN_BUDGET,
                    "tempo_segundos": time.monotonic() - inicio,
                    "erro": f"{type(exc).__name__}: {exc}",
                }
                self._log_metricas(self.ultima_execucao)
                if self.sessao_id:
                    atualizar_status_sessao(
                        self.sessao_id,
                        "falhou",
                        f"{self.nome}.erro_modelo",
                        self.ultima_execucao,
                        tarefa,
                        "[falha ao chamar o modelo]",
                    )
                registrar_execucao(
                    self.nome,
                    tarefa,
                    "[falha ao chamar o modelo]",
                    self.ultima_execucao,
                )
                raise

            if getattr(resposta, "usage", None):
                total_input_tokens += getattr(resposta.usage, "input_tokens", 0) or 0
                total_output_tokens += getattr(resposta.usage, "output_tokens", 0) or 0

            tokens_total = total_input_tokens + total_output_tokens
            if (
                resposta.stop_reason == "tool_use"
                and tokens_total >= config.TOKEN_BUDGET
            ):
                mensagem_erro = (
                    f"Orçamento de tokens atingido para o agente '{self.nome}': "
                    f"{tokens_total} de {config.TOKEN_BUDGET}. "
                    "A chamada de ferramenta e novas chamadas ao modelo foram interrompidas."
                )
                self._log(mensagem_erro)
                self.ultima_execucao = {
                    "passos": passo,
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "tokens_total": tokens_total,
                    "token_budget": config.TOKEN_BUDGET,
                    "tempo_segundos": time.monotonic() - inicio,
                    "erro": mensagem_erro,
                }
                self._log_metricas(self.ultima_execucao)
                if self.sessao_id:
                    atualizar_status_sessao(
                        self.sessao_id,
                        "limitado",
                        f"{self.nome}.limite_tokens",
                        self.ultima_execucao,
                        tarefa,
                        "[orçamento de tokens atingido]",
                    )
                registrar_execucao(
                    self.nome,
                    tarefa,
                    "[orçamento de tokens atingido]",
                    self.ultima_execucao,
                )
                raise RuntimeError(mensagem_erro)

            # Guardamos SEMPRE o conteúdo completo da resposta (não só o texto):
            # ele inclui os blocos de thinking e tool_use, que o modelo precisa
            # ver de novo na próxima chamada. O histórico só cresce, nunca é editado.
            if config.LLM_PROVIDER == "openrouter":
                mensagens.append(resposta.openrouter_message)
            else:
                mensagens.append({"role": "assistant", "content": resposta.content})

            if resposta.stop_reason == "refusal":
                self._log("o modelo recusou a tarefa.")
                self.ultima_execucao = {
                    "passos": passo,
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "tokens_total": tokens_total,
                    "token_budget": config.TOKEN_BUDGET,
                    "tempo_segundos": time.monotonic() - inicio,
                }
                self._log_metricas(self.ultima_execucao)
                if self.sessao_id:
                    atualizar_status_sessao(self.sessao_id, "recusado", f"{self.nome}.refusal", self.ultima_execucao, tarefa, "[recusado pelo modelo]")
                registrar_execucao(self.nome, tarefa, "[recusado pelo modelo]", self.ultima_execucao)
                return "[recusado pelo modelo]"

            if resposta.stop_reason == "max_tokens":
                self._log("resposta cortada por max_tokens.")
                self.ultima_execucao = {
                    "passos": passo,
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "tokens_total": tokens_total,
                    "token_budget": config.TOKEN_BUDGET,
                    "tempo_segundos": time.monotonic() - inicio,
                }
                self._log_metricas(self.ultima_execucao)
                resposta_final = _texto_final(resposta) + "\n[resposta truncada]"
                if self.sessao_id:
                    atualizar_status_sessao(self.sessao_id, "alerta", f"{self.nome}.max_tokens", self.ultima_execucao, tarefa, resposta_final)
                registrar_execucao(self.nome, tarefa, resposta_final, self.ultima_execucao)
                return resposta_final

            if resposta.stop_reason != "tool_use":
                # end_turn: o agente terminou.
                self._log(f"terminou em {passo} passo(s).")
                self.ultima_execucao = {
                    "passos": passo,
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "tokens_total": tokens_total,
                    "token_budget": config.TOKEN_BUDGET,
                    "tempo_segundos": time.monotonic() - inicio,
                }
                self._log_metricas(self.ultima_execucao)
                texto_final = _texto_final(resposta)
                if self.sessao_id:
                    atualizar_status_sessao(self.sessao_id, "concluida", f"{self.nome}.fim", self.ultima_execucao, tarefa, texto_final)
                registrar_execucao(self.nome, tarefa, texto_final, self.ultima_execucao)
                return texto_final

            # O modelo pediu uma ou mais ferramentas. Executamos todas e
            # devolvemos todos os resultados numa ÚNICA mensagem de usuário.
            tool_uses = [bloco for bloco in resposta.content if bloco.type == "tool_use"]
            with ThreadPoolExecutor(max_workers=min(len(tool_uses) or 1, config.MAX_TRABALHOS_PARARELOS)) as executor:
                resultados = list(executor.map(lambda bloco: self._executar_ferramenta(mapa_ferramentas, bloco), tool_uses))
            if config.LLM_PROVIDER == "openrouter":
                mensagens.extend(
                    {
                        "role": "tool",
                        "tool_call_id": resultado["tool_use_id"],
                        "content": (
                            f"Erro da ferramenta: {resultado['content']}"
                            if resultado.get("is_error")
                            else resultado["content"]
                        ),
                    }
                    for resultado in resultados
                )
            else:
                mensagens.append({"role": "user", "content": resultados})

        self.ultima_execucao = {
            "passos": config.MAX_PASSOS,
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "tokens_total": total_input_tokens + total_output_tokens,
            "token_budget": config.TOKEN_BUDGET,
            "tempo_segundos": time.monotonic() - inicio,
        }
        self._log_metricas(self.ultima_execucao)
        self._log(f"atingiu o limite de {config.MAX_PASSOS} passos.")
        if self.sessao_id:
            atualizar_status_sessao(self.sessao_id, "limitado", f"{self.nome}.limite", self.ultima_execucao, tarefa, "[limite de passos atingido sem resposta final]")
        registrar_execucao(self.nome, tarefa, "[limite de passos atingido sem resposta final]", self.ultima_execucao)
        return "[limite de passos atingido sem resposta final]"

    def _chamar_modelo(self, mensagens: list):
        if config.LLM_PROVIDER == "openrouter":
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": ferramenta.nome,
                        "description": ferramenta.descricao,
                        "parameters": ferramenta.parametros,
                    },
                }
                for ferramenta in self.ferramentas
            ]
            payload = {
                "model": config.MODELO,
                "messages": mensagens,
                "max_tokens": config.OPENROUTER_MAX_TOKENS,
            }
            if tools:
                payload["tools"] = tools
            return _normalizar_resposta_openrouter(client.chat.completions.create(**payload))

        payload = {
            "model": config.MODELO,
            "max_tokens": 16000,
            "system": self.system,
            "tools": [f.definicao_para_api() for f in self.ferramentas],
            "messages": mensagens,
        }

        if config.LLM_PROVIDER == "anthropic":
            payload["output_config"] = {"effort": self.effort}
            payload["betas"] = ["server-side-fallback-2026-07-01"]
            payload["fallbacks"] = "default"
        return client.messages.create(**payload)

    def _executar_ferramenta(self, mapa: dict, bloco) -> dict:
        args = bloco.input
        self._log(f"-> chamando ferramenta {bloco.name}({_resumo(str(args))})")

        ferramenta = mapa.get(bloco.name)
        if ferramenta is None:
            return _resultado(bloco.id, f"Ferramenta desconhecida: {bloco.name}", erro=True)

        try:
            saida = ferramenta.funcao(**args)
            if not isinstance(saida, str):
                raise TypeError(
                    f"a ferramenta '{bloco.name}' deve retornar str, "
                    f"mas retornou {type(saida).__name__}"
                )
        except Exception as e:  # o erro volta para o modelo, que pode corrigir
            mensagem_erro = (
                f"Erro ao executar ferramenta '{bloco.name}': "
                f"{type(e).__name__}: {e}"
            )
            self._log(f"<- {mensagem_erro}")
            return _resultado(bloco.id, mensagem_erro, erro=True)

        self._log(f"<- resultado: {_resumo(saida)}")
        return _resultado(bloco.id, saida)


# ------------------------------------------------------------------ helpers
def _resultado(tool_use_id: str, conteudo: str, erro: bool = False) -> dict:
    r = {"type": "tool_result", "tool_use_id": tool_use_id, "content": conteudo}
    if erro:
        r["is_error"] = True
    return r


def _normalizar_resposta_openrouter(resposta):
    """Adapta uma resposta Chat Completions ao formato interno do loop."""
    escolha = resposta.choices[0]
    mensagem = escolha.message
    blocos = []

    if mensagem.content:
        blocos.append(SimpleNamespace(type="text", text=mensagem.content))

    for chamada in mensagem.tool_calls or []:
        argumentos = json.loads(chamada.function.arguments or "{}")
        blocos.append(
            SimpleNamespace(
                type="tool_use",
                id=chamada.id,
                name=chamada.function.name,
                input=argumentos,
            )
        )

    motivo = {
        "tool_calls": "tool_use",
        "length": "max_tokens",
        "content_filter": "refusal",
    }.get(escolha.finish_reason, "end_turn")
    return SimpleNamespace(
        content=blocos,
        stop_reason=motivo,
        usage=SimpleNamespace(
            input_tokens=getattr(resposta.usage, "prompt_tokens", 0) or 0,
            output_tokens=getattr(resposta.usage, "completion_tokens", 0) or 0,
        ),
        openrouter_message=mensagem.model_dump(exclude_none=True),
    )


def _texto_final(resposta) -> str:
    return "\n".join(b.text for b in resposta.content if b.type == "text").strip()


def _resumo(texto: str, limite: int = 90) -> str:
    texto = " ".join(texto.split())
    return texto if len(texto) <= limite else texto[: limite - 3] + "..."


HISTORICO_PATH = Path(__file__).resolve().parent / ".historico_execucoes.json"
SESSOES_PATH = Path(__file__).resolve().parent / ".historico_sessoes.json"
ESTADO_EXECUCAO_PATH = Path(__file__).resolve().parent / ".estado_execucao.json"


def registrar_execucao(agente_nome: str, tarefa: str, resposta: str, metrica: dict) -> dict:
    """Persiste uma execução em disco para análise posterior."""
    caminho = HISTORICO_PATH
    if caminho.exists():
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            dados = []
    else:
        dados = []

    registro = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "agente": agente_nome,
        "tarefa": tarefa,
        "resposta": resposta,
        "metrica": metrica,
    }
    dados.append(registro)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return registro


def resumo_historico() -> dict:
    """Retorna um resumo do histórico persistido."""
    if not HISTORICO_PATH.exists():
        return {"total_execucoes": 0, "tempo_total_segundos": 0.0, "input_tokens_total": 0, "output_tokens_total": 0, "ultimas_execucoes": []}

    try:
        dados = json.loads(HISTORICO_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"total_execucoes": 0, "tempo_total_segundos": 0.0, "input_tokens_total": 0, "output_tokens_total": 0, "ultimas_execucoes": []}

    total_execucoes = len(dados)
    tempo_total = sum((item.get("metrica", {}).get("tempo_segundos", 0) or 0) for item in dados)
    input_total = sum((item.get("metrica", {}).get("input_tokens", 0) or 0) for item in dados)
    output_total = sum((item.get("metrica", {}).get("output_tokens", 0) or 0) for item in dados)
    ultimas = dados[-5:]
    return {
        "total_execucoes": total_execucoes,
        "tempo_total_segundos": round(tempo_total, 2),
        "input_tokens_total": input_total,
        "output_tokens_total": output_total,
        "ultimas_execucoes": ultimas,
    }


def _timestamp_agora() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def criar_sessao(sessao_id: str, pergunta: str | None = None, status: str = "iniciada") -> dict:
    """Cria ou atualiza um estado estruturado de sessão."""
    estado = ler_estado_execucao()
    estado.setdefault("sessoes", {})
    agora = _timestamp_agora()

    sessao = estado["sessoes"].setdefault(
        sessao_id,
        {
            "status": status,
            "pergunta_atual": pergunta,
            "ultima_pergunta": pergunta,
            "ultima_resposta": None,
            "ultima_etapa": None,
            "total_interacoes": 0,
            "ultima_metrica": {},
            "artefatos": [],
            "created_at": agora,
            "updated_at": agora,
        },
    )

    sessao["status"] = status
    if pergunta is not None:
        sessao["pergunta_atual"] = pergunta
        sessao["ultima_pergunta"] = pergunta
    sessao["updated_at"] = agora
    estado["ultimo_update"] = agora
    salvar_estado_execucao(estado)
    return sessao


def atualizar_status_sessao(sessao_id: str, status: str, etapa: str | None = None, metrica: dict | None = None, pergunta: str | None = None, resposta: str | None = None) -> dict:
    """Atualiza o estado operacional da sessão em andamento."""
    estado = ler_estado_execucao()
    estado.setdefault("sessoes", {})
    sessao = estado["sessoes"].setdefault(sessao_id, {"status": status, "ultima_pergunta": pergunta, "ultima_resposta": resposta, "ultima_etapa": etapa, "total_interacoes": 0, "ultima_metrica": metrica or {}, "artefatos": [], "created_at": _timestamp_agora(), "updated_at": _timestamp_agora()})

    agora = _timestamp_agora()
    sessao["status"] = status
    if etapa is not None:
        sessao["ultima_etapa"] = etapa
    if pergunta is not None:
        sessao["ultima_pergunta"] = pergunta
        sessao["pergunta_atual"] = pergunta
    if resposta is not None:
        sessao["ultima_resposta"] = resposta
    if metrica is not None:
        sessao["ultima_metrica"] = metrica
    sessao["updated_at"] = agora
    estado["ultimo_update"] = agora
    salvar_estado_execucao(estado)
    return sessao


def registrar_artefato(sessao_id: str, nome: str, tipo: str, conteudo: str, metadados: dict | None = None) -> dict:
    """Registra um artefato gerado na execução de uma sessão."""
    estado = ler_estado_execucao()
    estado.setdefault("sessoes", {})
    sessao = estado["sessoes"].setdefault(sessao_id, {"status": "iniciada", "ultima_pergunta": None, "ultima_resposta": None, "ultima_etapa": None, "total_interacoes": 0, "ultima_metrica": {}, "artefatos": [], "created_at": _timestamp_agora(), "updated_at": _timestamp_agora()})

    artefato = {
        "nome": nome,
        "tipo": tipo,
        "conteudo": conteudo,
        "metadados": metadados or {},
        "timestamp": _timestamp_agora(),
    }
    sessao.setdefault("artefatos", []).append(artefato)
    sessao["updated_at"] = artefato["timestamp"]
    estado["ultimo_update"] = artefato["timestamp"]
    salvar_estado_execucao(estado)
    return artefato


def registrar_etapa_execucao(sessao_id: str, etapa: str, status: str, detalhes: dict | None = None) -> dict:
    """Registra uma etapa dentro da execução de uma sessão."""
    estado = ler_estado_execucao()
    estado.setdefault("sessoes", {})
    sessao = estado["sessoes"].setdefault(
        sessao_id,
        {
            "status": "iniciada",
            "pergunta_atual": None,
            "ultima_pergunta": None,
            "ultima_resposta": None,
            "ultima_etapa": None,
            "total_interacoes": 0,
            "ultima_metrica": {},
            "artefatos": [],
            "historico_etapas": [],
            "created_at": _timestamp_agora(),
            "updated_at": _timestamp_agora(),
        },
    )

    evento = {
        "timestamp": _timestamp_agora(),
        "etapa": etapa,
        "status": status,
        "detalhes": detalhes or {},
    }
    sessao.setdefault("historico_etapas", []).append(evento)
    sessao["ultima_etapa"] = etapa
    sessao["status"] = status
    sessao["updated_at"] = evento["timestamp"]
    estado["ultimo_update"] = evento["timestamp"]
    salvar_estado_execucao(estado)
    return evento


def resumo_estado_execucao() -> dict:
    """Resumo compacto do estado persistido das sessões."""
    estado = ler_estado_execucao()
    sessoes = {}
    for sessao_id, sessao in estado.get("sessoes", {}).items():
        sessoes[sessao_id] = {
            "status": sessao.get("status"),
            "ultima_etapa": sessao.get("ultima_etapa"),
            "total_interacoes": sessao.get("total_interacoes", 0),
            "total_artefatos": len(sessao.get("artefatos", [])),
            "ultima_metrica": sessao.get("ultima_metrica", {}),
            "ultima_pergunta": sessao.get("ultima_pergunta"),
        }
    return {"ultimo_update": estado.get("ultimo_update"), "total_sessoes": len(sessoes), "sessoes": sessoes}


def registrar_sessao(sessao_id: str, pergunta: str, resposta: str, metrica: dict) -> dict:
    """Mantém um histórico por sessão para rastrear o contexto do usuário."""
    if SESSOES_PATH.exists():
        try:
            dados = json.loads(SESSOES_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            dados = {}
    else:
        dados = {}

    if sessao_id not in dados:
        dados[sessao_id] = []

    entrada = {
        "timestamp": _timestamp_agora(),
        "pergunta": pergunta,
        "resposta": resposta,
        "metrica": metrica,
    }
    dados[sessao_id].append(entrada)
    SESSOES_PATH.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    sessao = atualizar_status_sessao(
        sessao_id,
        status="concluida",
        etapa="final",
        metrica=metrica,
        pergunta=pergunta,
        resposta=resposta,
    )
    sessao["total_interacoes"] = len(dados[sessao_id])
    sessao["ultima_metrica"] = metrica
    estado = ler_estado_execucao()
    estado["sessoes"][sessao_id] = sessao
    salvar_estado_execucao(estado)
    registrar_artefato(sessao_id, "resposta_final", "texto", resposta, {"pergunta": pergunta, "metrica": metrica})
    registrar_etapa_execucao(sessao_id, "sessao.final", "concluida", {"pergunta": pergunta, "metrica": metrica})
    return entrada


def ler_estado_execucao() -> dict:
    """Lê o estado persistido da execução atual do sistema."""
    if not ESTADO_EXECUCAO_PATH.exists():
        return {"sessoes": {}, "ultimo_update": None, "versao": 1}

    try:
        return json.loads(ESTADO_EXECUCAO_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"sessoes": {}, "ultimo_update": None, "versao": 1}


def salvar_estado_execucao(estado: dict) -> None:
    """Grava o estado estruturado do sistema em disco."""
    ESTADO_EXECUCAO_PATH.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")


def resumo_sessoes() -> dict:
    """Retorna um resumo de todas as sessões salvas."""
    if not SESSOES_PATH.exists():
        return {"total_sessoes": 0, "sessoes": {}}

    try:
        dados = json.loads(SESSOES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"total_sessoes": 0, "sessoes": {}}

    estado = ler_estado_execucao()
    sessoes = {}
    for sessao_id, items in dados.items():
        item = estado.get("sessoes", {}).get(sessao_id, {})
        sessoes[sessao_id] = {
            "total_interacoes": len(items),
            "status": item.get("status", "concluida"),
            "ultima_etapa": item.get("ultima_etapa"),
            "ultima_pergunta": item.get("ultima_pergunta") or (items[-1].get("pergunta") if items else None),
            "ultima_resposta": item.get("ultima_resposta") or (items[-1].get("resposta") if items else None),
            "ultima_metrica": item.get("ultima_metrica") or (items[-1].get("metrica") if items else {}),
            "artefatos": item.get("artefatos", []),
        }

    return {
        "total_sessoes": len(dados),
        "sessoes": sessoes,
    }


def extrair_json(texto: str):
    """Extrai um JSON válido de um texto livre, mesmo com blocos Markdown."""
    if texto is None:
        raise ValueError("texto vazio para extração de JSON")

    text = str(texto).strip()
    if not text:
        raise ValueError("texto vazio para extração de JSON")

    bloco = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if bloco:
        text = bloco.group(1)

    candidatos = [text]
    if not text.startswith("{") and not text.startswith("["):
        posicoes = []
        for token in ("{", "["):
            pos = text.find(token)
            if pos != -1:
                posicoes.append(pos)
        if posicoes:
            inicio = min(posicoes)
            if text[inicio] == "{":
                fim = text.rfind("}")
            else:
                fim = text.rfind("]")
            if fim > inicio:
                candidatos.append(text[inicio : fim + 1])

    for candidato in candidatos:
        try:
            return json.loads(candidato)
        except json.JSONDecodeError:
            continue

    raise ValueError(f"Nenhum JSON válido encontrado em: {texto[:200]}")
