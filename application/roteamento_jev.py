"""Roteia perguntas para análise quantitativa ou resposta explicativa usando Jev."""

from typesafe_sdk import Choice, TypeSafeClient

import config


ROTAS = {"analisar", "explicar"}


def decidir_rota(pergunta: str, fatos: dict) -> dict:
    """Escolhe se a pergunta exige análise quantitativa ou explicação."""
    if not config.TYPESAFE_API_KEY:
        raise RuntimeError(
            "TYPESAFE_API_KEY não definida. Configure-a no arquivo .env."
        )

    with TypeSafeClient(model=config.TYPESAFE_MODEL) as client:
        resposta = client.system_one(
            state={"pergunta": pergunta, "fatos": fatos},
            questions={
                "rota": Choice(
                    instructions=(
                        "Com base na pergunta e nos fatos, decida qual etapa deve "
                        "ser executada antes de redigir a resposta."
                    ),
                    criteria={
                        "analisar": (
                            "A pergunta solicita ou depende de cálculos, estimativas "
                            "numéricas, comparação quantitativa ou resultado numérico."
                        ),
                        "explicar": (
                            "A pergunta pede definição, explicação conceitual ou "
                            "resumo factual sem cálculo quantitativo necessário."
                        ),
                    },
                )
            },
        )

    decisao = resposta.choices["rota"]
    if decisao.choice not in ROTAS:
        raise ValueError(f"Jev retornou uma rota inválida: {decisao.choice!r}")
    if not 0 <= decisao.confidence <= 1:
        raise ValueError(f"Jev retornou confiança inválida: {decisao.confidence!r}")

    return {
        "rota": decisao.choice,
        "confidence": decisao.confidence,
        "probabilities": decisao.probabilities,
    }
