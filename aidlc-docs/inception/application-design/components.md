# Componentes da Aplicação

## Visão geral

Este design define a arquitetura de alto nível para evoluir o protótipo atual em `application/` em direção à arquitetura-alvo da [SDD v5](../../../docs/sdd/sdd_orquestrador_agentes_v5.md). O objetivo é separar claramente: (1) entrada de eventos, (2) diagnóstico, (3) proposta de correção, (4) validação, (5) promoção e (6) auditoria.

## Componentes

### Escopo imediato — Maker-Checker e contratos de schema (R1)

#### `MakerCheckerService`
**Propósito:** coordenar um fluxo Maker -> validação determinística -> Checker -> validação determinística no protótipo atual.  
**Responsabilidades:**
- validar dados estruturados antes de invocar o Maker;
- validar a saída do Maker antes de encaminhá-la ao Checker;
- validar a saída do Checker e restringir decisões a valores permitidos;
- retornar sucesso somente depois que todas as validações determinísticas passarem.

#### `ContractValidator`
**Propósito:** analisar saída estruturada e validar dados contra schemas declarados.  
**Responsabilidades:**
- rejeitar JSON inválido, campos obrigatórios ausentes, tipos incorretos e valores inválidos;
- relatar falhas de validação explicitamente, sem convertê-las em sucesso do modelo;
- manter validação de contrato independente do julgamento do LLM.

Este incremento usa o runtime ReAct e os especialistas existentes. Não inclui
webhook/CI/CD, alteração de repositório, autorização externa, guardrails,
sandbox ou implantação.

### 1. `RuntimeOrchestrator`
**Propósito:** orquestrar o ciclo de execução do agente e o fluxo ReAct atual.  
**Responsabilidades:**
- coordenar especialistas e etapas do processo;
- controlar iterações, limites de token e métricas;
- coordenar a execução de ferramentas locais;
- publicar eventos de estado para a camada de observabilidade e auditoria.

**Interfaces principais:**
- `executar_fluxo(pergunta: str) -> str`
- `delegar_tarefa(agente: str, tarefa: str) -> str`
- `obter_resumo_execucao() -> dict`

### 2. `PipelineEventIngress`
**Propósito:** receber e validar o evento de falha do pipeline.  
**Responsabilidades:**
- receber payload de CI/CD;
- validar campos obrigatórios;
- normalizar dados para estrutura interna;
- rejeitar eventos incompletos ou inválidos.

**Interfaces principais:**
- `receber_evento(evento: dict) -> dict`
- `validar_payload(evento: dict) -> bool`

### 3. `FailureAnalyzer`
**Propósito:** analisar logs e contexto do repositório para identificar causa raiz.  
**Responsabilidades:**
- consolidar erro, logs e contexto de código;
- produzir achados estruturados;
- indicar severidade, local e evidência;
- distinguir achados confiáveis de hipóteses.

**Interfaces principais:**
- `analisar(erro: str, contexto_repo: dict) -> dict`
- `classificar_falha(logs: str) -> dict`

### 4. `PatchPlanner`
**Propósito:** gerar uma proposta de correção focalizada e segura.  
**Responsabilidades:**
- avaliar achados e escopo de mudança;
- limitar correção à causa raiz;
- produzir patch em formato estruturado;
- incluir justificativa e riscos esperados.

**Interfaces principais:**
- `propor_patch(falha: dict) -> dict`
- `validar_escopo(patch: dict) -> bool`

### 5. `RegressionTester`
**Propósito:** executar validações e testes de regressão em ambiente isolado.  
**Responsabilidades:**
- preparar ambiente de execução;
- rodar testes relevantes;
- coletar resultados e evidências;
- bloquear avanço quando a validação falha.

**Interfaces principais:**
- `executar_validacao(patch: dict, ambiente: str) -> dict`
- `coletar_resultados() -> dict`

### 6. `QualityGateEvaluator`
**Propósito:** aplicar critérios determinísticos para liberação de ambientes.  
**Responsabilidades:**
- avaliar status das validações;
- controlar regras de progresso por ambiente;
-expedir aprovação ou bloqueio com base em evidência objetiva.

**Interfaces principais:**
- `avaliar(resultado_teste: dict, contexto: dict) -> dict`
- `aplicar_regra(gate: str, resultado: dict) -> bool`

### 7. `PromotionManager`
**Propósito:** coordenar promoção entre DEV, STAGING e PROD.  
**Responsabilidades:**
- decidir avanço por ambiente;
- exigir aprovação humana para produção;
- orquestrar comunicação de status para a equipe.

**Interfaces principais:**
- `promover(decisao: dict) -> dict`
- `solicitar_aprovacao_producao() -> dict`

### 8. `AuditTrail`
**Propósito:** manter histórico imutável ou, no mínimo, append-only, dos eventos e decisões.  
**Responsabilidades:**
- registrar eventos de entrada, diagnóstico, patch, testes e aprovação;
- manter traços de causalidade entre evento e decisão;
- apoiar revisão posterior por auditoria e governança.

**Interfaces principais:**
- `registrar(evento: str, dados: dict) -> dict`
- `consultar(evento_id: str) -> dict`

## Padrões de composição

- O `RuntimeOrchestrator` permanece como camada de execução do protótipo, mas deve evoluir para uma orquestração de workflow de auto-remediação.
- No R1, `MakerCheckerService` coordena trabalhadores existentes e `ContractValidator` valida cada fronteira antes do avanço.
- O raciocínio do modelo deve ser separado da autorização e decisão determinística.
- Cada etapa do fluxo deve produzir artefatos estruturados: diagnóstico, patch, teste e decisão de promoção.
- O registro em `AuditTrail` deve ser usado como fonte de verdade para observabilidade e auditoria.
- Webhooks, autorização externa, guardrails, sandbox e promoção permanecem como arquitetura-alvo futura.
