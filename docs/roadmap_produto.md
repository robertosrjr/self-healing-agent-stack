# Roadmap do Produto

## Objetivo

Este roadmap organiza a evolução do projeto de estudo para a arquitetura-alvo
de orquestração corporativa e auto-remediação de CI/CD descrita no
[SDD v5](./sdd/sdd_orquestrador_agentes_v5.md). Ele serve para acompanhar
marcos, evidências e decisões de prontidão; não representa um compromisso de
datas de entrega.

O objetivo do produto é coordenar agentes especializados para analisar falhas
e alterações de código, produzindo diagnósticos, propostas e resultados
verificáveis. Controles determinísticos devem continuar responsáveis por
autorizações, gates de qualidade e promoções de ambiente.

## Situação atual

- **Base existente:** protótipo didático do runtime ReAct e do padrão
  orquestrador-trabalhadores; o Passo 1 está documentado como concluído em
  [plano do runtime](./plano_passo_1_runtime.md).
- **Planejamento:** requisitos, design e unidades de trabalho foram
  documentados em `aidlc-docs/`.
- **Implementação do produto-alvo:** ainda não iniciada. O protótipo não recebe
  eventos de CI/CD, não diagnostica repositórios, não gera/aplica patches e
  não executa gates ou promoções corporativas.
- **Incremento de aprendizado mais recente:** o Passo 2 de padrões multiagente
  está concluído no protótipo, incluindo paralelo entre agentes, *handoff* e
  planejamento Magentic. O próximo marco do roadmap do produto continua sendo
  R2 — autorização determinística e guardrails; esse marco não se confunde com
  o Passo 2 do estudo.

## Marcos

| Marco | Escopo e resultado esperado | Critérios de conclusão | Situação |
|---|---|---|---|
| **R0 — Runtime ReAct** | Consolidar o ciclo modelo-ferramenta-observação, limites de execução, tratamento explícito de falhas e registro de métricas. | Comportamentos principais exercitados por testes automatizados e registrados no plano do Passo 1. | **Concluído** como protótipo didático |
| **R1 — Maker-Checker e contratos** | Criar um fluxo sequencial em que um agente produz um resultado e outro o revisa, com validação de esquema nas entradas e saídas. | Saídas válidas prosseguem; conteúdo inválido ou fora do contrato interrompe o fluxo explicitamente; testes cobrem ambos os caminhos. | **Concluído** como incremento local; 29 testes passaram |
| **R2 — Autorização e guardrails** | Adicionar controles determinísticos externos ao LLM, com política *deny-by-default* e verificações de entrada e saída para conteúdo malicioso, segredos e dados pessoais. | Ações não autorizadas são bloqueadas; casos de guardrail têm testes; falhas não são tratadas como aprovação. | **Planejado** |
| **R3 — Ingressão e diagnóstico** | Definir e validar o evento de falha; relacionar logs e contexto do repositório; produzir diagnóstico estruturado com causa provável, evidências e severidade. | Payload inválido é rejeitado; diagnóstico tem contrato verificável e evidências rastreáveis; nenhuma alteração de código é executada nesta etapa. | **Planejado** |
| **R4 — Proposta de correção e QA isolado** | Produzir uma proposta de patch limitada à causa identificada e executar testes de regressão em ambiente isolado. | A proposta tem escopo e justificativa; testes existentes e novos passam antes de qualquer avanço; falhas interrompem a promoção. | **Planejado** |
| **R5 — Integração com eventos e STAGING** | Integrar gatilhos de CI/CD, preparar PR e habilitar progressão controlada para DEV/STAGING após os quality gates. | Eventos e resultados ficam associados à execução; gates determinísticos autorizam ou bloqueiam o avanço; evidências de teste acompanham a mudança. | **Planejado** |
| **R6 — Governança de Produção** | Completar o plano de controle, trilha de auditoria e processo de aprovação para Produção. | Promoção a Produção exige aprovação humana explícita, além dos gates; decisões, aprovações e bloqueios são auditáveis. | **Planejado** |

Os marcos R1 e R2 refletem a sequência de aprendizado definida nas diretrizes
do projeto. R3 a R6 organizam as fases da SDD v5: diagnóstico, correção e QA,
integração com eventos e STAGING, e governança de Produção.

## Acompanhamento de cada marco

Ao iniciar um marco, registrar escopo e responsável no planejamento de
execução. Ao concluí-lo, atualizar a situação desta tabela e anexar ou
referenciar evidências verificáveis:

- critérios de aceite atendidos ou pendentes;
- testes executados e seus resultados;
- contratos, achados e decisões produzidos;
- riscos conhecidos, bloqueios e dependências;
- decisão de prosseguir, revisar ou interromper.

Um marco só deve ser considerado concluído quando seus critérios forem
demonstrados por testes ou evidências revisáveis. A conclusão de um marco de
aprendizado não significa que o produto esteja pronto para produção.

## Indicadores do produto

Os documentos de arquitetura não definem baselines nem metas numéricas para
estes indicadores. Primeiro estabelecer uma linha de base em execuções
controladas; em seguida, definir metas antes de qualquer piloto operacional.

| Indicador | O que acompanhar |
|---|---|
| **Qualidade do diagnóstico** | Proporção de diagnósticos aceitos por revisores e correspondência entre causa apontada e evidências da falha. |
| **Qualidade da correção proposta** | Proporção de propostas consideradas focadas e aceitas para validação, sem expansão injustificada de escopo. |
| **Sucesso de regressão** | Proporção de execuções em que testes existentes e novos passam; acompanhar separadamente falhas legítimas e falhas do ambiente de teste. |
| **Tempo de diagnóstico e remediação** | Tempo entre o evento de falha, o diagnóstico revisado e a conclusão da validação; não confundir com economia já comprovada. |
| **Segurança dos gates** | Tentativas bloqueadas por falta de autorização, guardrail ou evidência suficiente, e promoções bloqueadas por testes ou política. |
| **Rastreabilidade** | Proporção de execuções com evento, achados, proposta, testes, decisão de gate e aprovação registrados conforme o escopo implementado. |

## Guardrails de progresso

- O LLM pode analisar e propor; não decide sua própria autorização nem aprova
  um merge ou uma promoção.
- Manutenção ou mutação de repositório e infraestrutura requer autorização
  determinística explícita.
- Testes inválidos, falhas de segurança ou ausência de evidências bloqueiam o
  avanço; não devem produzir resultados com aparência de sucesso.
- Promoção para Produção exige aprovação humana explícita, além dos quality
  gates determinísticos.
- Limites atuais do protótipo (`MAX_PASSOS=10` e `TOKEN_BUDGET=20000` por
  execução de agente) não equivalem aos limites de evento propostos no SDD.

## Fontes

- [SDD v5 — arquitetura-alvo consolidada](./sdd/sdd_orquestrador_agentes_v5.md)
- [SDD v2 — versão histórica](./sdd/sdd_orquestrador_agentes_v2.md)
- [Diretrizes e visão arquitetural do estudo](./sdd/diretrizes_estudo_orquestracao_agentes.md)
- [Plano do Passo 1 — runtime ReAct](./plano_passo_1_runtime.md)
- Requisitos e decomposição em unidades de trabalho mantidos em `aidlc-docs/`.
