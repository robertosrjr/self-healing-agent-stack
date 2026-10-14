# Dependências entre Unidades de Trabalho

## Matriz de Dependência

| Unidade | Depende de | Observação |
|---|---|---|
| U1 — Maker-Checker e Contratos de Schema | Nenhuma unidade anterior | Usa o runtime ReAct existente (R0), já implementado |
| U2 — Ingressão e Diagnóstico de Falhas | U1 | Requer contratos e coordenação de trabalhadores |
| U3 — Proposta de Correção e Escopo | U2 | Depende do diagnóstico estruturado |
| U4 — Validação, Gate e Promoção | U3 | Depende da proposta validada e da Política |

## Pontos de integração

- `MakerCheckerService` valida entradas e saídas dos trabalhadores por meio de `ContractValidator`.
- O runtime existente executa os trabalhadores sem conceder autoridade para mutação ou promoção.
- `PipelineEventIngress` alimenta o fluxo de U2 com eventos validados e contexto de execução.
- `FailureAnalyzer` produz achados em formato estruturado para `PatchPlanner`.
- `PatchPlanner` emite patch e justificativa para `RegressionTester`.
- `QualityGateEvaluator` usa o resultado dos testes para decidir avanço do ambiente.
- `PromotionManager` consulta a política de aprovação e registra a decisão no histórico.

## Ordem de construção recomendada

1. U1 — Maker-Checker e Contratos de Schema
2. U2 — Ingressão e Diagnóstico de Falhas
3. U3 — Proposta de Correção e Escopo
4. U4 — Validação, Gate e Promoção

R0 (runtime ReAct) é a base já construída. Essa ordem reduz risco, valida
contratos entre agentes antes de introduzir eventos ou ações mutáveis e mantém
governança e promoção em incrementos posteriores.
