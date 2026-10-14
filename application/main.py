"""
Ponto de entrada.

Uso:
    python main.py                       # usa a pergunta de exemplo
    python main.py "sua pergunta aqui"
"""

import json
import sys

from agente import ler_estado_execucao, registrar_sessao, resumo_estado_execucao, resumo_historico, resumo_sessoes
from orquestrador import executar_fluxo_padrao, orquestrador

PERGUNTA_EXEMPLO = (
    "Vale a pena colocar energia solar numa casa comum no Brasil? "
    "Quero saber quantos painéis eu preciso, quanto custa e em quanto tempo "
    "o investimento se paga. Responda em no máximo 150 palavras."
)


def main() -> None:
    pergunta = " ".join(sys.argv[1:]) or PERGUNTA_EXEMPLO
    sessao_id = "sessao-default"
    print(f"\nPERGUNTA: {pergunta}\n" + "=" * 70)

    resposta = executar_fluxo_padrao(pergunta)

    # Compatibilidade com o padrão anterior: se o modelo resolver sozinho, ainda
    # funciona, mas o fluxo programado agora é o padrão de execução do projeto.
    if not resposta or resposta.strip() == "":
        resposta = orquestrador.executar(pergunta)

    print("=" * 70 + f"\nRESPOSTA FINAL:\n\n{resposta}\n")

    historico = resumo_historico()
    registrar_sessao(sessao_id, pergunta, resposta, {"total_execucoes": historico.get("total_execucoes", 0)})

    historico = resumo_historico()
    sessoes = resumo_sessoes()
    estado = ler_estado_execucao()
    resumo_execucao = resumo_estado_execucao()

    print("=" * 70)
    print("HISTÓRICO RESUMIDO:")
    print(json.dumps(historico, ensure_ascii=False, indent=2))
    print("=" * 70)
    print("SESSÕES:")
    print(json.dumps(sessoes, ensure_ascii=False, indent=2))
    print("=" * 70)
    print("ESTADO EXECUÇÃO:")
    print(json.dumps(estado, ensure_ascii=False, indent=2))
    print("=" * 70)
    print("RESUMO EXECUÇÃO:")
    print(json.dumps(resumo_execucao, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
