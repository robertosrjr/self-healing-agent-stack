---
name: code-quality-guidance
description: "Use when reviewing or refactoring Python for SOLID, maintainability, typing, error handling, naming, and testability."
---

# Qualidade de Código Python

Ajude a manter o código Python legível, tipado quando isso melhorar a
compreensão, testável e coerente com os padrões já usados no repositório.

## SOLID na prática Python

| Princípio | Aplicação |
|---|---|
| Single Responsibility | Funções e classes com motivos claros para mudar. |
| Open/Closed | Composição, funções/strategies ou Protocols quando novos comportamentos reais surgirem. |
| Liskov Substitution | Implementações de Protocols preservam semântica e contratos, não apenas assinaturas. |
| Interface Segregation | Protocols pequenos e específicos; não criar interfaces sem consumidor alternativo. |
| Dependency Inversion | Casos de uso recebem dependências necessárias por construtor/parâmetro e não criam SDKs globalmente. |

## Convenções Python

- Use `snake_case` para funções e variáveis, `PascalCase` para classes e nomes
  que expressem intenção.
- Use type hints onde aumentem clareza e facilitem verificação; não use casts
  para esconder tipos incorretos.
- Prefira funções pequenas com uma responsabilidade; limites como 15–20 linhas
  são heurísticos, não regras automáticas.
- Use `None` apenas quando representa ausência e modele-a com `T | None`;
  prefira exceções ou coleções vazias quando semanticamente adequadas.
- Use `dataclass` para objetos de domínio simples; Pydantic para validação de
  fronteiras conforme os contratos já escolhidos no R1.
- Evite estado global mutável e inicialização de clientes externos no import
  de módulos quando isso comprometer testes ou composição.
- Não capture exceções amplamente para continuar com resposta aparentemente
  válida. Capture apenas para acrescentar contexto ou traduzir a fronteira e
  preserve a causa com `raise ... from exc`.

## Padrões sem abstração prematura

| Padrão | Opção idiomática | Use quando |
|---|---|---|
| Strategy | Callable/Protocol | Implementações realmente intercambiáveis |
| Adapter | Função/classe adaptadora | Isolar SDK ou protocolo externo |
| Factory | Função de composição | Construção depende de configuração |
| Decorator | Decorator Python | Comportamento transversal reutilizável |
| Chain of Responsibility | Etapas explicitamente compostas | Pipeline com fases independentes |

Prefira injeção simples de funções se abstrações formais não trouxerem
benefício demonstrável. Não use padrões sem necessidade concreta.

## Qualidade automatizada

Mantenha os comandos e ferramentas existentes. Ruff pode cobrir lint/format e
mypy ou Pyright podem verificar tipos, mas não introduza essas ferramentas sem
decisão de projeto e configuração explícitas. A suíte atual usa pytest:

```powershell
python -m pytest tests -q
```

Ao revisar, explique problemas concretos, proponha alterações focadas e rode a
verificação mais curta que cubra o comportamento modificado.
