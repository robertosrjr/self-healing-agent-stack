---
name: sre-observability-skill
description: "Use when reviewing observability for Python systems: structured logs, latency, traffic, errors, saturation, tracing, SLO evidence, and telemetry privacy."
---

# Observabilidade SRE para Python

Coordene a análise de logs, métricas, traces e evidências operacionais.
Diferencie sempre o protótipo Python local da futura plataforma de
auto-remediação descrita na SDD v5.

## Workflow

1. Inventarie chamadas a `logging`, `print`, SDKs externos e armazenamento de
   métricas/traces efetivamente configurados.
2. Mapeie latência, tráfego, erros e saturação para componentes que realmente
   recebem carga operacional.
3. Verifique correlação por identificadores de execução e, se distribuído,
   trace/span IDs.
4. Revise cardinalidade, amostragem, retenção e minimização de dados sensíveis.
5. Proponha a menor mudança mensurável; não adicione telemetria de produção ao
   protótipo sem requisitos ou consumidor definido.
6. Execute testes focados e informe riscos residuais e SLOs apenas quando
   existirem medidas e metas acordadas.

## Regras

- Use dimensões estáveis e de baixa cardinalidade; nunca IDs, prompts ou PII
  como labels de métricas.
- Não registre conteúdo integral de prompts, respostas, contexto de repositório
  ou chaves de API por conveniência.
- `print` existente no protótipo não equivale a logging estruturado ou trilha
  de auditoria confiável.
- Use as skills agnósticas de [logging](../agnostic-logging/SKILL.md),
  [metrics](../agnostic-metrics/SKILL.md),
  [tracing](../agnostic-tracing/SKILL.md) e
  [privacy](../agnostic-privacy/SKILL.md) como referências especializadas.
- Coordene limites de chamadas com
  [resiliência](../resilience-checker-skill/SKILL.md) e privacidade com
  [LGPD](../lgpd-sre-compliance-skill/SKILL.md).

## Estado do projeto

O R1 é executado localmente, sem API HTTP, exporters de métricas/traces ou
SLOs operacionais definidos. A instrumentação de chamadas LLM, workers,
execuções de pipeline e auditoria pertence a marcos futuros e deve evitar
confundir métricas de aprendizado com evidência de produção.
