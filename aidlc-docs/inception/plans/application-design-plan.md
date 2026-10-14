# Plano de Design da Aplicação

## Objetivo

Definir a estrutura de componentes e serviços para evoluir o protótipo atual em `application/` para a arquitetura-alvo da SDD v5, começando pelo incremento Maker-Checker com schemas validados.

## Checklist de Execução

- [x] Revisar requisitos e histórias do usuário
- [x] Identificar componentes principais
- [x] Definir responsabilidades e interfaces
- [x] Descrever serviços de orquestração
- [x] Mapear dependências e fluxos de dados
- [x] Validar consistência do design e escopo incremental
- [x] Gerar artefatos finais

## Áreas de Design

### 1. Componentes principais

- [x] `PipelineEventIngress` — componente-alvo para receber e validar evento de falha
- [x] `FailureAnalyzer` — componente-alvo para analisar contexto autorizado do repositório
- [x] `PatchPlanner` — componente-alvo para propor correção focada e limitada
- [x] `RegressionTester` — componente-alvo para validar correção em ambiente isolado
- [x] `QualityGateEvaluator` — componente-alvo para critérios determinísticos de avanço
- [x] `PromotionManager` — componente-alvo; Produção requer aprovação humana além dos gates
- [x] `AuditTrail` — componente-alvo para registro protegido e auditável
- [x] `RuntimeOrchestrator` — integra agentes especialistas e loop ReAct atual
- [x] `MakerCheckerService` — escopo imediato para coordenar Maker/Checker
- [x] `ContractValidator` — escopo imediato para validar schemas de entrada e saída

### 2. Serviços de orquestração

- [x] `SelfHealingService` — alvo futuro; coordena ciclo de remediação completo
- [x] `DiagnosticService` — alvo futuro; consolida falha e evidências
- [x] `PatchService` — alvo futuro; estrutura proposta de correção
- [x] `ValidationService` — alvo futuro; executa testes e mede resultados
- [x] `PolicyService` — alvo futuro; política externa, gates e aprovação
- [x] `AuditService` — alvo futuro; registra a cadeia de evidências
- [x] `ContractValidationService` — escopo imediato; valida contratos versionados
- [x] `MakerCheckerService` — escopo imediato; compõe o fluxo sequencial

### 3. Interfaces e assinaturas

- [x] Interfaces dos componentes-alvo documentadas em `component-methods.md`
- [x] Interfaces de `MakerCheckerService` e `ContractValidator` documentadas em `component-methods.md`

### 4. Dependências e padrões de comunicação

- [x] Fluxo de eventos entre ingressão, diagnóstico e orquestração documentado como alvo
- [x] Dependência da camada de controle determinístico sobre a camada de agente de IA
- [x] Separação entre raciocínio, validação de schema e autorização documentada
- [x] Comunicação estruturada; persistência local atual diferenciada da auditoria-alvo

## Perguntas de Design

### Q1: Qual camada deve ser o ponto de entrada do sistema para eventos de falha?
A. Webhook HTTP dedicado  
B. Trigger de CI/CD diretamente integrado ao runner  
C. Entrada por fila assíncrona / broker  
D. Outra (descreva)  

[Answer]: B

### Q2: A validação de código deve ficar em uma camada separada do orquestrador principal?
A. Sim, com camada dedicada de QA e gates  
B. Não, tudo fica na mesma orquestração principal  
C. Parcialmente, com camada dedicada apenas para testes críticos  
D. Outra (descreva)  

[Answer]: A

### Q3: Qual nível de autonomia deve existir para promoção para DEV/STAGING?
A. Autonomia total após gates determinísticos  
B. Validação humana obrigatória em todos os avanços  
C. Ambos, com DEV/STAGING automatizados e PROD com aprovação humana  
D. Outra (descreva)  

[Answer]: C

## Resultado Esperado

A aplicação-alvo será organizada em componentes de entrada, diagnóstico, correção, validação, promoção e auditoria. O primeiro incremento implementável limita-se a Maker-Checker e validação de schemas no runtime local; não inclui webhook, mutação, autorização externa ou guardrails. A aprovação de Produção exige intervenção humana além dos quality gates, conforme a SDD v5.
