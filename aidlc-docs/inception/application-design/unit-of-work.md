# Unidades de Trabalho

## Visão geral

A decomposição separa o runtime didático já concluído (R0) dos incrementos
futuros em direção à arquitetura-alvo definida pela
[SDD v5](../../../docs/sdd/sdd_orquestrador_agentes_v5.md). A primeira unidade
nova é o marco R1 Maker-Checker; webhook, autorização, guardrails e promoção
permanecem fora dessa entrega inicial.

## U1 — Maker-Checker e Contratos de Schema

**Objetivo:** acrescentar ao runtime existente uma coordenação Maker-Checker
com validação explícita de entradas e saídas estruturadas.

**Responsabilidades:**
- validar dados de entrada antes da invocação do Maker;
- analisar e validar a saída do Maker antes de encaminhá-la ao Checker;
- analisar e validar a saída do Checker antes de retornar resultado;
- interromper o fluxo com erro explícito diante de payload inválido,
  incompleto ou inconclusivo.

**Componentes envolvidos:**
- `MakerCheckerService`;
- `ContractValidator`;
- agentes Maker e Checker;
- runtime ReAct existente como infraestrutura de execução.

**Critérios de conclusão:**
- contratos de entrada, saída do Maker e decisão do Checker definidos;
- JSON inválido, campos ausentes e tipos/valores inválidos não avançam;
- o resultado só é aceito se satisfizer o contrato determinístico do Checker;
- testes existentes continuam passando.

**Fora do escopo:** webhook, eventos CI/CD, mutação de repositório, worktree,
autorização externa, guardrails, sandbox e deploy.

## U2 — Ingressão e Diagnóstico de Falhas

**Objetivo:** transformar eventos autorizados de falha de pipeline em
diagnósticos estruturados.

**Responsabilidades:**
- receber e validar eventos CI/CD;
- analisar logs e contexto de repositório autorizado;
- produzir achados com severidade, evidência e incerteza.

**Componentes envolvidos:** `PipelineEventIngress`, `FailureAnalyzer`,
`AuditTrail`.

**Critérios de conclusão:** eventos válidos geram diagnósticos rastreáveis;
eventos inválidos são rejeitados; evidência insuficiente não produz diagnóstico
com aparência de certeza.

## U3 — Proposta de Correção e Escopo

**Objetivo:** propor uma correção focada em ambiente isolado e vinculada à
causa identificada.

**Responsabilidades:** limitar o escopo da proposta; preservar commit-base;
registrar justificativa, evidências e riscos; impedir aplicação sem autorização.

**Componentes envolvidos:** `PatchPlanner`, `SelfHealingService`, worktree,
`AuditTrail`.

## U4 — Validação, Gate e Promoção

**Objetivo:** validar propostas e controlar progressão por ambientes.

**Responsabilidades:** Maker-Checker de domínio, QA independente, execução
isolada, gates determinísticos, PR, promoção autorizada e aprovação humana de
Produção.

**Componentes envolvidos:** `BusinessDomainWorker`, `RegressionTester`,
`QualityGateEvaluator`, `PromotionManager`, `AuditTrail`.

## Mapeamento de histórias

- US-01 -> U2
- US-02 -> U2
- US-03 -> U3
- US-04 -> U4
- US-05 -> U4
- US-06 -> U4
- US-07 -> U1

## Cobertura e dependências

Cada história está atribuída a exatamente uma unidade principal. U1 usa o
runtime já existente como pré-requisito R0; U2 depende dos contratos de U1,
U3 depende do diagnóstico de U2 e U4 depende da proposta de U3.
