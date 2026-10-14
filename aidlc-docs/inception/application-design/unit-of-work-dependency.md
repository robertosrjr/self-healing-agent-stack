# Dependências entre Unidades de Trabalho

## Matriz de Dependência

| Unidade | Depende de | Observação |
|---|---|---|
| U1 — Runtime e Orquestração Base | Nenhuma | Base funcional atual do protótipo |
| U2 — Ingressão e Diagnóstico de Falhas | U1 | Requer runtime e estruturas de estado |
| U3 — Proposta de Correção e Escopo | U2 | Depende do diagnóstico estruturado |
| U4 — Validação, Gate e Promoção | U3 | Depende da proposta validada e da Política |

## Pontos de integração

- `RuntimeOrchestrator` alimenta `PipelineEventIngress` e `AuditTrail` com contexto de execução.
- `FailureAnalyzer` produz achados em formato estruturado para `PatchPlanner`.
- `PatchPlanner` emite patch e justificativa para `RegressionTester`.
- `QualityGateEvaluator` usa o resultado dos testes para decidir avanço do ambiente.
- `PromotionManager` consulta a política de aprovação e registra a decisão no histórico.

## Ordem de construção recomendada

1. U1 — Runtime e Orquestração Base
2. U2 — Ingressão e Diagnóstico de Falhas
3. U3 — Proposta de Correção e Escopo
4. U4 — Validação, Gate e Promoção

Essa ordem reduz risco, preserva a base funcional e deixa a validação e a governança como camada final de proteção.
