# Software Design Document (SDD): Sistema Orquestrador de Agentes de IA Corporativo e Esteira de Auto-Remediação (Self-Healing)

**Versão:** 2.0  
**Status:** Aprovado para Construção  
**Escopo:** Arquitetura de Orquestração Multi-Agente, Reativação por Eventos, Esteira de Revisão de Código e Agente de Auto-Remediação (Self-Healing)  

---

## 1. Visão Geral e Princípios de Design

### 1.1 Propósito
Este documento especifica a arquitetura técnica, contratos de interface e padrões de execução para a implementação do **Sistema Orquestrador de Agentes de IA Corporativo**, englobando tanto a **Esteira de Revisão de Código (SDLC)** quanto o subsistema de **Auto-Remediação de Pipelines (Self-Healing)**.

O objetivo fundamental é fechar a lacuna de confiança (*Trust Gap*) entre a capacidade do modelo generativo e a execução operacional em produção. O sistema combina análise probabilística orientada por IA com controle determinístico de infraestrutura, garantindo resiliência, auditabilidade e segurança contra falhas e comportamentos indesejados.

### 1.2 Princípios Arquiteturais Fundamentais
* **Separação Rígida entre Inteligência e Controle:** O Modelo de Linguagem (LLM) atua exclusivamente como motor de raciocínio. Decisões de autorização, acesso a ferramentas, mutações no código e promoção de ambientes são gerenciadas e auditadas pelo Plano de Controle (*Control Plane*).
* **Delegação com Contexto Isolado:** O agente orquestrador gerencia sub-agentes especialistas via invocação de ferramentas (*tool calling*). Cada especialista é executado em uma sessão isolada contendo apenas o contexto necessário para sua tarefa específica, evitando poluição de janela e alucinações.
* **Arquitetura Orientada a Eventos (Reativa):** Além da atuação interativa, o orquestrador permanece em estado ocioso (*idle*) e é estimulado automaticamente por gatilhos de falha de CI/CD (Webhooks/Serverless Functions) para iniciar rotinas de auto-remediação.
* **Política de Acesso Restrito (*Deny-by-Default*):** Nenhuma ferramenta ou ação mutável no repositório ou infraestrutura é executada sem validação prévia e explícita pelo Ponto de Aplicação de Política (PEP) utilizando políticas Cedar/IAM.
* **Autonomia Graduada com *Human-in-the-Loop*:** Correções, testes de regressão e implantações em ambientes de Desenvolvimento (DEV) e Homologação (STAGING) operam de forma autônoma (Tiers T1–T3). A promoção final para **Produção (PROD)** exige validação humana obrigatória (*Human-in-the-Loop*) ou aprovação por *Quality Gate* determinístico estrito.
* **Resiliência e Determinismo de Runtime:** Toda iteração de agente é limitada por travas de profundidade (`MAX_PASSOS`), limite de tokens (`token_budget`), timeouts por chamada e mecânica de *rollback* em caso de falha nos testes de regressão.

---

## 2. Arquitetura de Sistemas em 3 Planos

```
+----------------------------------------------------------------------------------+
|                         PLANO DE CONTROLE (CONTROL PLANE)                        |
|   +------------------------+  +-------------------------+  +------------------+   |
|   |  Input Guardrails      |  | PEP / PDP (Cedar/IAM)   |  | Output Guardrails|   |
|   | (Segurança & PII)      |  |  (Deny-by-Default)      |  | (PII & Segredos) |   |
|   +-----------+------------+  +------------+------------+  +--------+---------+   |
+---------------+----------------------------+------------------------+------------+
                |                            |                        |
+---------------+----------------------------+------------------------+------------+
|               v                            v                        v            |
|  +----------------------------------------------------------------------------+  |
|  |                    PLANO DE EXECUÇÃO (RUNTIME REACTION)                    |  |
|  |                                                                            |  |
|  |  +----------------------------------------------------------------------+  |  |
|  |  |                    ORQUESTRADOR CENTRAL (ReAct)                      |  |  |
|  |  |              (Think -> Plan -> Act -> Observe -> Score)               |  |  |
|  |  +-------+------------------+------------------+------------------+-----+  |  |
|  |          |                  |                  |                  |        |  |
|  |          v                  v                  v                  v        |  |
|  |  +---------------+  +---------------+  +---------------+  +-------------+  |  |
|  |  |  Diagnóstico  |  | Desenvolvedor |  | QA & Testes   |  | Implantação |  |  |
|  |  |  (Stack/Log)  |  | (Patch/Diff)  |  |  Regressivos  |  | & Promoção  |  |  |
|  |  +---------------+  +---------------+  +---------------+  +-------------+  |  |
|  +----------------------------------------------------------------------------+  |
|                                                                                  |
+----------------------------------------------------------------------------------+
                                         |
+----------------------------------------+-----------------------------------------+
|                        PLANO DE CICLO DE VIDA (LLMOps & SDLC)                    |
|   +-----------------------+  +--------------------------+  +-------------------+  |
|   | Trilha de Auditoria   |  | Avaliação Offline (Pass^k|  | Quality Gates     |  |
|   | Imutável (Audit Trail)|  | & Benchmarks)            |  | Determinísticos   |  |
|   +-----------------------+  +--------------------------+  +-------------------+  |
+----------------------------------------------------------------------------------+
```

### 2.1 Plano de Execução (Runtime)
* **Laço ReAct Dinâmico:** Cada agente executa a cadeia de raciocínio e ação `Think -> Plan -> Act -> Observe -> Score`.
* **Motor de Reativação por Eventos:** Escuta requisições HTTP/Webhooks vindos do CI/CD contendo informações sobre falhas de build ou teste (`pipeline_id`, `commit_hash`, `error_log`).
* **Gerenciamento Concorrente:** Utiliza `ThreadPoolExecutor` para disparar análises paralelas (ex.: diagnóstico de log e busca na base de código) sem bloquear o fluxo principal.
* **Isolamento de Memória & Contexto:** O histórico completo do orquestrador não é exposto aos sub-agentes. Cada trabalhador recebe apenas uma carga útil (*payload*) autocontida.

### 2.2 Plano de Controle (Control Plane & Governança)
* **Ponto de Aplicação de Política (PEP):** Intercepta todas as invocações de ferramentas (`tool_calls`), consultando o Ponto de Decisão de Política (PDP) para autorizar ações de leitura, escrita, commit e deploy.
* **Filtros de Entrada (*Input Guardrails*):** Analisam o log de erro e arquivos do repositório para evitar manipulações indiretas em dados de exceção.
* **Filtros de Saída (*Output Guardrails*):** Impedem que chaves de API, segredos ou dados pessoais (PII) vazem para os logs ou comentários de PRs.

### 2.3 Plano de Ciclo de Vida (LLMOps / SDLC)
* **Quality Gates Determinísticos:** Regras condicionais rígidas executadas fora do LLM que avaliam o resultado das suites de teste e cobertura antes de autorizar avanço de ambiente.
* **Avaliação $Pass^k$:** Benchmarks contínuos medindo a taxa de correção de código sem introdução de novos bugs.
* **Trilha de Auditoria (*Audit Trail*):** Registro de proveniência em banco de dados imutável registrando a cadeia completa de raciocínio, diffs gerados, comandos de teste executados e aprovações humanas.

---

## 3. Design Detalhado dos Componentes do Agente de Auto-Remediação

### 3.1 Orquestrador de Auto-Remediação (`SelfHealingOrchestrator`)
* **Gatilho:** Invocado via Webhook por falha na esteira de CI/CD.
* **Responsabilidade:** Coordena o ciclo de vida da remediação (Diagnóstico -> Patch -> Teste -> Homologação -> Solicitação de Produção).
* **Catálogo de Ferramentas Nativas:**
  * `delegar(agente_alvo, instrucao, contexto)`: Invoca sub-agentes em sessão isolada.
  * `registrar_registro_tarefa(task_id, status)`: Mantém o estado dinâmico da execução (*Task Ledger*).
  * `notificar_equipe(canal, mensagem, severidade)`: Envia alertas para Slack/Teams sobre falhas e pedidos de aprovação em Produção.

### 3.2 Sub-Agentes Especialistas da Esteira de Remediação

1. **Agente de Diagnóstico e Causa Raiz (`DiagnosticWorker`)**
   * *Função:* Baixar os logs de execução da esteira, analisar o *stack trace*, identificar o arquivo/linha do erro e buscar o contexto relevante no código-fonte.
   * *Saída:* Relatório estruturado do erro com identificação do bug e contexto do código.

2. **Agente Desenvolvedor e Correção (`DevFixWorker`)**
   * *Função:* Gerar o patch de correção (*code diff*) focado exclusivamente na causa raiz apontada pelo diagnóstico, mantendo o padrão arquitetural da aplicação.
   * *Saída:* Diff de código e arquivos modificados.

3. **Agente de QA e Testes de Regressão (`QARegressionWorker`)**
   * *Função:* Criar automaticamente novos cenários de testes de unidade ou integração que reproduzam a falha original e comprovem a eficácia do patch, executando a suite de testes no ambiente de Desenvolvimento.
   * *Saída:* Suíte de testes criada e relatório de execução (`PASSED` / `FAILED`).

4. **Agente de Implantação e Promoção (`DeploymentPromotionWorker`)**
   * *Função:* Criar branch de remediação (`fix/auto-healing-id`), realizar o commit, abrir Pull Request e disparar a implantação automatizada para o ambiente de Homologação (Staging). Para Produção, gera a solicitação formal de aprovação.
   * *Saída:* PR criado, build de Staging promovido e solicitação de PROD submetida.

---

## 4. Contratos de Interface e Schemas

### 4.1 Evento de Falha da Esteira (`PipelineFailureEventSchema`)
```json
{
  "title": "PipelineFailureEventSchema",
  "type": "object",
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "pipeline_id": { "type": "string" },
    "repository_url": { "type": "string" },
    "branch": { "type": "string" },
    "commit_hash": { "type": "string" },
    "environment": { "type": "string", "enum": ["DEV", "STAGING", "PROD"] },
    "failure_stage": { "type": "string", "enum": ["BUILD", "UNIT_TEST", "INTEGRATION_TEST", "SECURITY_SCAN"] },
    "error_log_raw": { "type": "string" },
    "triggered_at": { "type": "string", "format": "date-time" }
  },
  "required": ["event_id", "pipeline_id", "repository_url", "branch", "commit_hash", "failure_stage", "error_log_raw"]
}
```

### 4.2 Relatório do Agente de Auto-Remediação (`SelfHealingReportSchema`)
```json
{
  "title": "SelfHealingReportSchema",
  "type": "object",
  "properties": {
    "healing_id": { "type": "string", "format": "uuid" },
    "pipeline_id": { "type": "string" },
    "root_cause_analysis": {
      "type": "object",
      "properties": {
        "error_type": { "type": "string" },
        "affected_files": { "type": "array", "items": { "type": "string" } },
        "description": { "type": "string" }
      },
      "required": ["error_type", "affected_files", "description"]
    },
    "patch_applied": {
      "type": "object",
      "properties": {
        "branch_created": { "type": "string" },
        "diff_content": { "type": "string" }
      },
      "required": ["branch_created", "diff_content"]
    },
    "regression_tests": {
      "type": "object",
      "properties": {
        "test_files_added": { "type": "array", "items": { "type": "string" } },
        "execution_status": { "type": "string", "enum": ["PASSED", "FAILED"] },
        "coverage_percentage": { "type": "number" }
      },
      "required": ["test_files_added", "execution_status"]
    },
    "promotion_status": {
      "type": "object",
      "properties": {
        "dev_status": { "type": "string", "enum": ["DEPLOYED", "FAILED"] },
        "staging_status": { "type": "string", "enum": ["DEPLOYED", "FAILED", "SKIPPED"] },
        "prod_promotion_request": {
          "type": "object",
          "properties": {
            "required_approval": { "type": "boolean", "default": True },
            "approval_status": { "type": "string", "enum": ["PENDING", "APPROVED", "REJECTED"] },
            "approver_id": { "type": "string" }
          }
        }
      }
    }
  },
  "required": ["healing_id", "pipeline_id", "root_cause_analysis", "patch_applied", "regression_tests", "promotion_status"]
}
```

### 4.3 Contrato Universal de Achados (`FindingContract`)
```json
{
  "title": "FindingContract",
  "type": "object",
  "properties": {
    "finding_id": { "type": "string" },
    "category": { 
      "type": "string",
      "enum": ["ARCHITECTURE", "CODE_QUALITY", "SECURITY", "COMPLIANCE", "RUNTIME_ERROR"]
    },
    "severity": {
      "type": "string",
      "enum": ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    },
    "location": { "type": "string" },
    "description": { "type": "string" },
    "remediation_suggestion": { "type": "string" }
  },
  "required": ["finding_id", "category", "severity", "description"]
}
```

---

## 5. Diagrama de Sequência do Agente de Auto-Remediação

```
[CI/CD Pipeline]      [Function Trigger]     [Orquestrador]    [Diagnóstico]     [DevFix]       [QA & Testes]    [Deploy/Staging]    [Aprovador Humano]
       |                       |                  |                 |               |                 |                 |                   |
       |--- Falha no Build --->|                  |                 |               |                 |                 |                   |
       |    (Error Logs)       |--- Webhook ----->|                 |               |                 |                 |                   |
       |                       |    (Event Payload)                 |               |                 |                 |                   |
       |                       |                  |-- Delegar ----->|               |                 |                 |                   |
       |                       |                  |   Análise Log   |               |                 |                 |                   |
       |                       |                  |<-- StackTrace --|               |                 |                 |                   |
       |                       |                  |    + Causa Raiz                 |                 |                 |                   |
       |                       |                  |                                 |                 |                 |                   |
       |                       |                  |-- Delegar Patch de Código ----->|                 |                 |                   |
       |                       |                  |<-- Code Diff / Fix -------------|                 |                 |                   |
       |                       |                  |                                                   |                 |                   |
       |                       |                  |-- Delegar Testes de Regressão ------------------->|                 |                   |
       |                       |                  |<-- Testes Adicionados & Executados (PASSED) ------|                 |                   |
       |                       |                  |                                                                     |                   |
       |                       |                  |-- Deploy & Commit em Staging -------------------------------------->|                   |
       |                       |                  |<-- Staging Deploy OK (Tier T3) -------------------------------------|                   |
       |                       |                  |                                                                                         |
       |                       |                  |-- Criar Solicitação de Promoção para PROD (Tier T2) ----------------------------------->|
       |                       |                  |   (Anexa Relatório de Testes & Audit Trail)                                             |
       |                       |                  |                                                                                         |
       |                       |                  |<-- Aprovação de 1-Clique do Engenheiro / Lead ------------------------------------------|
       |                       |                  |                                                                                         |
       |<----------------------┴------------------┴-- Executar Implantação Automatizada em PROD -----------------------------------------------|
```

---

## 6. Governança, Autonomia Graduada e Segurança

### 6.1 Matriz de Autonomia Graduada Aplicada ao Self-Healing

| Nível (*Tier*) | Escopo de Ação Permitido | Regras de Governança e Portões de Segurança |
| :--- | :--- | :--- |
| **Tier T1 (Probatório)** | Leitura de logs e análise de causa raiz | Leitura estrita de logs de erro e código. Nenhuma alteração permitida. |
| **Tier T2 (Supervisionado)** | Promoção para **PRODUÇÃO** | Exige **aprovação humana obrigatória (*Human-in-the-Loop*)** ou *Quality Gate* determinístico estrito. |
| **Tier T3 (Confiável)** | Patch, Testes e Deploy em **DEV / STAGING** | Execução autônoma de criação de branch, fix, geração de testes de regressão e deploy em Homologação. |
| **Tier T4 (Autônomo)** | Autocorreção de infraestrutura leve em Staging | Restrito a ambientes de não-produção com auditoria assíncrona pós-execução. |

### 6.2 Regra de Promoção e Rebaixamento
* **Condição de Promoção:** O agente só avança o código para o ambiente seguinte se 100% dos testes existentes + os novos testes de regressão passarem com sucesso.
* **Rebaixamento Imediato:** Qualquer tentativa de alteração fora do escopo do bug, falha de segurança detectada por SAST ou injeção de prompt rebaixa o agente imediatamente para **Tier T1**, cancelando a execução e notificando a equipe de segurança.

### 6.3 Travas Operacionais e Limites de Runtime
* `MAX_PASSOS` por sub-agente: 5 iterações ReAct.
* `MAX_HEALING_ATTEMPTS`: Máximo de 2 tentativas de correção automática por falha para evitar loops infinitos de build.
* `TOKEN_BUDGET_PER_HEALING`: 25.000 tokens por evento de falha.
* `SANDBOX_ISOLATION`: O patch e os testes são compilados e executados dentro de containers efémeros isolados sem acesso à rede externa.

---

## 7. Roteiro de Implementação

* **Fase 1 (Core ReAct & Diagnostic Worker):** Implementar o laço ReAct base com captura de logs de erro e identificação de causa raiz no código.
* **Fase 2 (DevFix & QA Workers):** Desenvolver a lógica de geração de diff de código e criação automatizada de suítes de testes de regressão.
* **Fase 3 (Gatilho por Evento & Staging Deploy):** Integrar o webhook de gatilho do CI/CD e a automação de commit, PR e implantação em ambiente de Homologação (STAGING - Tier T3).
* **Fase 4 (Governança PROD & Control Plane):** Adicionar a validação de política *Deny-by-Default* (PEP), a interface de aprovação humana (*Human-in-the-Loop*) para Produção (Tier T2) e o registro imutável na Trilha de Auditoria.
