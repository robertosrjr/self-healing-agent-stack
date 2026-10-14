# Unidades de Trabalho

## Visão geral

A decomposição foi feita para evoluir o protótipo atual em etapas pequenas e verificáveis, preservando a arquitetura-alvo do SDD v2.

## U1 — Runtime e Orquestração Base
**Objetivo:** manter e evoluir o loop ReAct do protótipo atual como base de execução.  
**Responsabilidades:**
- manter o runtime de agentes e especialista;
- consolidar métricas e histórico de execução;
- orquestrar fluxo principal do prompt para resposta;
- preparar integração com eventos e contexto do pipeline.

**Componentes envolvidos:**
- `RuntimeOrchestrator`
- `AuditTrail` (parte do registro de execução)

**Critérios de conclusão:**
- o runtime continua funcionando com o protótipo atual;
- o fluxo de execução consegue registrar eventos estruturados;
- a base do agente permanece compatível com os testes existentes.

## U2 — Ingressão e Diagnóstico de Falhas
**Objetivo:** transformar falhas de pipeline em diagnósticos estruturados.  
**Responsabilidades:**
- receber eventos de CI/CD;
- validar payloads;
- analisar logs e contexto do repositório;
- produzir achados com severidade e evidência.

**Componentes envolvidos:**
- `PipelineEventIngress`
- `FailureAnalyzer`
- `AuditTrail`

**Critérios de conclusão:**
- evento de falha é convertido em diagnóstico estruturado;
- dados de contexto e logs são relacionados de forma compreensível;
- a saída do diagnóstico está pronta para a etapa de patch.

## U3 — Proposta de Correção e Escopo
**Objetivo:** estabelecer a camada de patch focado e seguro.  
**Responsabilidades:**
- transformar a causa raiz em proposta de mudança;
- controlar escopo e evitar correções amplas;
- preparar artefatos de revisão e justificativa.

**Componentes envolvidos:**
- `PatchPlanner`
- `SelfHealingService` (parte da coordenação)
- `AuditTrail`

**Critérios de conclusão:**
- a correção é limitada ao problema identificado;
- a proposta inclui justificativa e risco conhecido;
- a proposta fica pronta para validação por testes.

## U4 — Validação, Gate e Promoção
**Objetivo:** garantir que o patch seja validado antes de avançar entre ambientes.  
**Responsabilidades:**
- executar testes de regressão;
- aplicar regras de qualidade determinísticas;
- controlar promoção de DEV/STAGING e PROD;
- registrar aprovação e bloqueios.

**Componentes envolvidos:**
- `RegressionTester`
- `QualityGateEvaluator`
- `PromotionManager`
- `AuditTrail`

**Critérios de conclusão:**
- existe evidência objetiva de testes e gate;
- promoções exigem aprovação conforme o ambiente;
- bloqueios ficam documentados no histórico de auditoria.

## Mapeamento de histórias

- US-01 -> U2
- US-02 -> U2
- US-03 -> U3
- US-04 -> U4
- US-05 -> U4
- US-06 -> U1 + U4

## Cobertura

Todas as histórias foram atribuídas a exatamente uma unidade principal, com rastreio para auditoria e governança. O conjunto fornece um caminho incremental e verificável do protótipo atual para a arquitetura de Self-Healing.
