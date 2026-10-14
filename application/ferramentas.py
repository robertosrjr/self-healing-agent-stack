"""
Ferramentas simples que os especialistas podem usar.

São propositalmente "de brinquedo" e locais (sem internet), para você focar
na orquestração. Troque por coisas reais depois (busca na web, banco de dados...).
"""

import ast
import operator

from agente import Ferramenta

# ---------------------------------------------------------------- base local
# Uma "base de conhecimento" fake. O pesquisador só sabe o que está aqui.
BASE_DE_CONHECIMENTO = {
    "energia solar": (
        "Painéis solares fotovoltaicos convertem luz em eletricidade. Um painel "
        "residencial típico tem 550 W de potência. No Brasil, a média de sol "
        "pleno é de cerca de 5 horas por dia. O custo instalado gira em torno "
        "de R$ 4,00 por watt."
    ),
    "consumo residencial": (
        "Uma residência brasileira média consome cerca de 160 kWh por mês. "
        "A tarifa média de energia é de aproximadamente R$ 0,85 por kWh."
    ),
    "carro eletrico": (
        "Um carro elétrico compacto consome cerca de 15 kWh a cada 100 km. "
        "Um motorista médio roda 1.000 km por mês."
    ),
}


def buscar_na_base(termo: str) -> str:
    termo = termo.lower()
    achados = [f"{chave}: {texto}" for chave, texto in BASE_DE_CONHECIMENTO.items()
               if termo in chave or any(p in chave for p in termo.split())]
    if not achados:
        return f"Nada encontrado para '{termo}'. Tópicos disponíveis: {list(BASE_DE_CONHECIMENTO)}"
    return "\n".join(achados)


# ---------------------------------------------------------------- calculadora
# Avalia expressões aritméticas com segurança (sem usar eval()).
_OPERADORES = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
}


def _avaliar(no):
    if isinstance(no, ast.Constant) and isinstance(no.value, (int, float)):
        return no.value
    if isinstance(no, ast.BinOp) and type(no.op) in _OPERADORES:
        return _OPERADORES[type(no.op)](_avaliar(no.left), _avaliar(no.right))
    if isinstance(no, ast.UnaryOp) and type(no.op) in _OPERADORES:
        return _OPERADORES[type(no.op)](_avaliar(no.operand))
    raise ValueError("expressão não suportada (use só números e + - * / **)")


def calcular(expressao: str) -> str:
    resultado = _avaliar(ast.parse(expressao, mode="eval").body)
    return f"{expressao} = {round(resultado, 4)}"


# ---------------------------------------------------------------- contador
def contar_palavras(texto: str) -> str:
    return f"{len(texto.split())} palavras"


# ---------------------------------------------------------------- definições
BUSCAR = Ferramenta(
    nome="buscar_na_base",
    descricao="Busca fatos na base de conhecimento local. Use termos curtos, ex.: 'energia solar'.",
    parametros={
        "type": "object",
        "properties": {"termo": {"type": "string", "description": "Termo de busca"}},
        "required": ["termo"],
    },
    funcao=buscar_na_base,
)

CALCULAR = Ferramenta(
    nome="calcular",
    descricao="Calcula uma expressão aritmética, ex.: '550 * 5 * 30 / 1000'. Use sempre que fizer contas.",
    parametros={
        "type": "object",
        "properties": {"expressao": {"type": "string", "description": "Expressão com + - * / **"}},
        "required": ["expressao"],
    },
    funcao=calcular,
)

CONTAR_PALAVRAS = Ferramenta(
    nome="contar_palavras",
    descricao="Conta quantas palavras um texto tem.",
    parametros={
        "type": "object",
        "properties": {"texto": {"type": "string"}},
        "required": ["texto"],
    },
    funcao=contar_palavras,
)
