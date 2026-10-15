# Verificações de Segurança — U1 Maker-Checker

## Escopo

Estas verificações cobrem somente controles presentes no incremento local:
rejeição de campos extras, validação fail-closed, não exposição de valores
rejeitados e impedimento de delegação direta dos agentes Maker e Checker pelo
orquestrador genérico.

Elas não constituem auditoria de segurança, nem validam proteção completa
contra prompt injection, autorização, sandbox, rate limiting, segurança de
dependências ou operação em produção.

## Execução

A partir da pasta `application/`:

```powershell
python -m pytest tests/test_maker_checker.py -q
```

Confirme que os testes de contrato e os testes de orquestração passam. Em
particular, falhas de parsing/schema não devem invocar o worker dependente ou
incluir valores rejeitados na mensagem de erro.

## Limitações e próximos controles

- O delimitador de dados externos e o escape textual são medidas de separação
  de contexto, não uma defesa completa contra prompt injection.
- Não há entrada HTTP, autorização externa, credenciais de escopo reduzido,
  política de retenção ou auditoria imutável neste incremento.
- Reavalie os controles ao adicionar R2 (guardrails e autorização) e qualquer
  integração com repositório, CI/CD, rede ou execução de código.
