---
name: architecture-guidance
description: "Use when designing Python package boundaries, ports and adapters, DDD models, or reviewing dependency direction and architecture."
---

# Arquitetura Python: Hexagonal e DDD

Use esta skill para desenhar ou revisar limites entre domínio, casos de uso e
integrações em aplicações Python. A estrutura proposta é uma opção para
evoluções que precisem dela, não uma exigência de reorganizar o protótipo atual.

## Regra de dependência

```text
adapters/infrastructure -> application -> domain
```

- Domínio contém regras e tipos de negócio puros; não importa SDKs, web
  frameworks, Pydantic, armazenamento ou clientes externos.
- Aplicação coordena casos de uso e depende do domínio e de contratos/ports.
- Adaptadores implementam integração com modelos, HTTP, persistência, filas e
  filesystem; ficam na borda do sistema.
- Dependências de runtime são montadas no ponto de composição, não escondidas
  em imports globais.

## Estrutura Python possível

Para uma aplicação que cresça além do protótipo em módulos planos:

```text
application/
  domain/
    models.py
    exceptions.py
    services.py
  use_cases/
    maker_checker.py
    ports.py
  adapters/
    llm/
    http/
    persistence/
  config.py
tests/
```

Não criar camadas vazias apenas para reproduzir um diagrama. A estrutura atual
usa módulos Python diretamente em `application/`; mudanças arquiteturais devem
ser incrementais e motivadas por dependências ou responsabilidades concretas.

## Ports e adapters em Python

Use `typing.Protocol` quando uma abstração estrutural for útil para trocar
implementações ou testar um caso de uso. Funções injetadas também são
suficientes para dependências simples, como os workers de `MakerCheckerService`.
Não introduza interfaces nominais para cada função por padrão.

```python
from typing import Protocol


class MakerWorker(Protocol):
    def executar(self, tarefa: str) -> str: ...


class ExecutarMakerChecker:
    def __init__(self, maker: MakerWorker) -> None:
        self._maker = maker
```

Contratos externos podem usar Pydantic na borda; não faça o domínio depender de
modelos Pydantic quando tipos imutáveis ou dataclasses forem suficientes.

## DDD com parcimônia

| Conceito | Aplicação em Python | Quando usar |
|---|---|---|
| Entity | Classe/dataclass com identidade explícita | Ciclo de vida e identidade importam |
| Value Object | `dataclass(frozen=True, slots=True)` ou tipo imutável | Validar e comparar por valor |
| Aggregate | Entidade raiz que protege invariantes | Há invariantes transacionais relacionadas |
| Repository port | `Protocol` na aplicação; adapter na borda | Persistência real é necessária |
| Domain service | Função/classe sem dependência de infraestrutura | Regra não pertence a uma entidade |
| Domain event | Dataclass/evento imutável | Consumidores precisam reagir sem acoplamento |
| Bounded context | Pacotes/modelos separados | Linguagem e regras divergem entre contextos |

Não adote entidades, agregados ou event sourcing apenas por estarem no
vocabulário DDD. O R1 atual coordena validação Maker-Checker local e ainda não
tem persistência ou bounded contexts implantados.

## Validação arquitetural

- Escreva testes de importação/arquitetura para as regras que forem importantes.
- `import-linter` é uma opção se o projeto vier a adotar uma ferramenta
  específica; declarar a dependência e configurar contratos somente quando
  houver módulos/camadas reais para proteger.
- Mantenha testes unitários puros para domínio e testes de casos de uso com
  ports ou workers falsos.

## Como responder

1. Descreva as dependências reais e o estado atual antes de propor camadas.
2. Identifique violações concretas da direção de dependência.
3. Recomende a menor mudança que melhora isolamento e testabilidade.
4. Não atribua ao protótipo capacidades-alvo ainda não implementadas.
