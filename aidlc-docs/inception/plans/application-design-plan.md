# Plano de Design da Aplicação

## Objetivo

Definir a estrutura de componentes e serviços para evoluir o protótipo atual em `application/` para o fluxo de auto-remediação orientado ao SDD v2.

## Checklist de Execução

- [ ] Revisar requisitos e histórias do usuário
- [ ] Identificar componentes principais
- [ ] Definir responsabilidades e interfaces
- [ ] Descrever serviços de orquestração
- [ ] Mapear dependências e fluxos de dados
- [ ] Validar consistência do design
- [ ] Gerar artefatos finais

## Áreas de Design

### 1. Componentes principais

- [ ] `PipelineEventIngress` — recebe e valida evento de falha do pipeline
- [ ] `FailureAnalyzer` — interpreta logs e contexto do repositório para diagnosticar causa raiz
- [ ] `PatchPlanner` — propõe correção focada e limitada ao escopo necessário
- [ ] `RegressionTester` — executa testes e valida a correção em ambiente isolado
- [ ] `QualityGateEvaluator` — aplica critérios determinísticos para avanço de ambiente
- [ ] `PromotionManager` — coordena DEV/STAGING/PROD e a aprovação human-in-the-loop
- [ ] `AuditTrail` — mantém registro imutável de eventos, decisões e artefatos
- [ ] `RuntimeOrchestrator` — integra os agentes especialistas e o loop ReAct do protótipo atual

### 2. Serviços de orquestração

- [ ] `SelfHealingService` — coordenador do ciclo completo de diagnóstico, correção, testes e promoção
- [ ] `DiagnosticService` — consolida logs, contexto e evidências de falha
- [ ] `PatchService` — gera e estrutura proposta de correção
- [ ] `ValidationService` — executa testes e mede resultados
- [ ] `PolicyService` — gerencia gates, autorização e aprovação externa
- [ ] `AuditService` — registra a cadeia de evidências e decisões

### 3. Interfaces e assinaturas

- [ ] `PipelineEventIngress.receber_evento(evento: dict) -> dict`
- [ ] `FailureAnalyzer.analisar(erro: str, contexto_repo: dict) -> dict`
- [ ] `PatchPlanner.propor_patch(falha: dict) -> dict`
- [ ] `RegressionTester.executar_validacao(patch: dict, ambiente: str) -> dict`
- [ ] `QualityGateEvaluator.avaliar(resultado_teste: dict, contexto: dict) -> dict`
- [ ] `PromotionManager.promover(decisao: dict) -> dict`
- [ ] `AuditTrail.registrar(evento: str, dados: dict) -> dict`

### 4. Dependências e padrões de comunicação

- [ ] Fluxo de eventos entre ingressão, diagnóstico e orquestração
- [ ] Dependência da camada de controle determinístico sobre a camada de agente de IA
- [ ] Separação clara entre raciocínio do modelo e autorização de ações de mutação
- [ ] Comunicação de dados estruturados entre serviços e persistência local

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

A aplicação será organizada em componentes de entrada, diagnóstico, correção, validação, promoção e auditoria, com serviços de orquestração separados e dependências explícitas. Isso preserva a arquitetura-alvo do SDD v2 sem misturar decisões de IA com políticas determinísticas.
