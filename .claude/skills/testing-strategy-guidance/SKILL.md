---
name: testing-strategy-guidance
description: "Use for Python developer-level tests, pytest, TDD, unit and integration testing, and enforceable architecture rules. For product QA strategy and CI/CD gates, use quality-assurance-skills."
---

# Testes Python: TDD e Estratégia

Use esta skill para testes de código Python e para propor uma estratégia
proporcional à arquitetura existente. O projeto executa a suíte em `application/`
com `python -m pytest tests -q`; os testes atuais usam `unittest.TestCase` e
`unittest.mock` e são executados pelo pytest.

## Ciclo TDD

1. **RED:** escreva um teste que demonstre o comportamento ausente.
2. **GREEN:** implemente a menor mudança que o faça passar.
3. **REFACTOR:** simplifique mantendo os testes verdes.

Não escreva testes dependentes de um provedor LLM real para validar lógica de
contrato ou orquestração.

## Pirâmide adequada ao sistema

- **Unitários:** maioria; validações Pydantic, regras de domínio e sequência de
  casos de uso com dependências injetadas.
- **Integração:** quando houver adapters reais, como banco, HTTP ou broker;
  teste os limites concretos sem substituir toda a camada sob teste.
- **End-to-end:** poucos cenários críticos somente quando existir uma jornada
  integrada de aplicação.

O protótipo local não exige containers de teste, serviços externos, testes HTTP
ou E2E. Não adicione infraestrutura de teste sem uma integração real a validar.

## Estilo pytest

Use nomes que expressem condição e resultado, organização Arrange-Act-Assert,
fixtures compartilhadas com parcimônia, e `pytest.mark.parametrize` para casos
de dados relacionados:

```python
import pytest


@pytest.mark.parametrize(
    ("decision", "expected_status"),
    [("APPROVED", "APPROVED"), ("REJECTED", "REJECTED")],
)
def test_checker_decision_sets_response_status(decision, expected_status):
    result = build_response(decision)

    assert result["status"] == expected_status
```

Para falhas, use `pytest.raises`; para patching use `monkeypatch` ou
`unittest.mock.patch`. Injete fakes/stubs na fronteira do serviço e não faça
mock do objeto que está sendo testado.

## Casos relevantes para fluxos de agentes

- Contratos: campos ausentes/extras, tipo inválido, enum inválido, JSON inválido,
  limites e erro sem ecoar valores rejeitados.
- Orquestração: chamadas na ordem esperada; não chamar o próximo worker após
  falha; decisões válidas permanecem distintas de erros.
- Falhas: exceções externas propagam explicitamente, sem sucesso alternativo.
- Segurança do fluxo: agentes com privilégios/ferramentas diferentes não devem
  ter caminhos alternativos que contornem validações.
- Testes não fazem chamadas de rede nem exigem chaves reais.

## Integração e ferramentas opcionais

- `pytest` é o runner já usado no repositório.
- `unittest.mock` faz parte da biblioteca padrão; prefira monkeypatch/fakes
  simples quando forem suficientes.
- `pytest-cov`, `hypothesis`, `httpx` ou ferramentas de containers só devem ser
  adicionados quando um objetivo de cobertura, propriedade ou integração
  justificar a dependência.
- Ferramentas de regras de importação podem proteger camadas se o projeto
  evoluir para uma arquitetura de pacotes explícita.

Comando documentado a partir de `application/`:

```powershell
python -m pytest tests -q
```

Não invente meta de cobertura universal. Defina metas por risco e comportamento
crítico quando a equipe também passar a medir cobertura.
