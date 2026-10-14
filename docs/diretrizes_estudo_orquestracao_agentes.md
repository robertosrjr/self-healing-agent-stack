# Diretrizes e Visão Arquitetural: Orquestração de Agentes de IA em Ambientes Corporativos

## Executive Summary & Propósito
Este documento consolida a visão arquitetural, os princípios de segurança, os padrões de orquestração e o roteiro prático de aprendizado sobre **Orquestração de Agentes de IA Corporativos**. O objetivo deste material é servir como documento de referência e memória de conhecimento para o projeto, permitindo que a base de conhecimento seja constantemente alinhada com as diretrizes e intenções do estudo.

---

## 1. O Conceito Central e a Resolução do "Trust Gap"
A transição de modelos de linguagem isolados para **Sistemas de Agentes de IA** marca a passagem da geração passiva de texto para a execução ativa de tarefas operacionais em ambientes corporativos.

* **LLM Passivo (Passagem Única / Stateless):** Responde a perguntas com base em seu conhecimento pré-treinado ou no contexto imediato enviado no prompt, sem capacidade direta de ação externa.
* **Agente de IA (Stateful / Multi-tool):** Combina um modelo de base (*Foundation Model*) com memória persistente, catálogo de ferramentas (APIs, scripts, bancos de dados, RAG) e capacidade de raciocínio iterativo e planejamento.
* **O Trust Gap (Lacuna de Confiança):** Refere-se à distância entre o que um agente *pode* teoricamente fazer e o que a organização *confia* que ele execute de forma segura. A orquestração existe fundamentalmente para fechar essa lacuna através de governança, auditabilidade e controles determinísticos.

---

## 2. A Pilha do Sistema de Agentes (*Enterprise Agent Stack*) e os 3 Planos
Para garantir que a imprevisibilidade probabilística do modelo não comprometa a estabilidade dos sistemas organizacionais, a arquitetura é dividida em **três planos independentes**:

### A. Plano de Execução (Runtime)
* **Laço Dinâmico ReAct:** O agente opera em um laço de reflexão e ação (**Think ➔ Plan ➔ Act ➔ Observe ➔ Score**).
* **Isolamento de Sessão:** Cada interação roda em ambiente isolado (como microVMs ou containers), prevenindo vazamento de dados entre usuários ou locatários.
* **Execução Durável:** Suporte a checkpoints, gerenciamento de estado e retomada assíncrona para fluxos de longa duração.

### B. Plano de Controle (Control Plane & Governança)
* **Princípio Deny-by-Default:** A autorização de ferramentas ocorre de forma externa ao LLM (usando motores de política como Cedar ou IAM). O modelo nunca decide suas próprias permissões.
* **Metadados de Risco das Ferramentas:** As ferramentas possuem atributos estáticos (ex: *side_effect*, *reversibility*, *egress*) e atributos dinâmicos do recurso (*environment*, *data_classification*) avaliados pelo Ponto de Aplicação de Política (PEP).
* **Guardrails em Tempo Real:** Filtros de entrada (*Input Guardrails* contra injeção de prompt) e filtros de saída (*Output Guardrails* para mascaramento de segredos e PII).

### C. Plano de Ciclo de Vida (LLMOps / SDLC)
* **Gestão de Prompts e Políticas:** Versionamento e testes contínuos de prompts, regras e modelos.
* **Conjuntos de Avaliação (*Benchmarks*):** Testes de regressão e medição de eficácia por meio de métricas como $Pass^k$ e taxa de sucesso da tarefa (*Task Completion Rate*).
* **Testes Adversariais (*Red Teaming*):** Simulação contínua de tentativas de *jailbreak* e sequestro de agente (*hijacking*).

---

## 3. Unidade Básica: O Laço ReAct e Controles de Runtime (Passo 1 do Estudo)
A unidade fundamental de qualquer agente é o laço dinâmico de raciocínio e ação:

1. **Think (Pensar):** O modelo analisa a intenção do usuário e o histórico da conversa.
2. **Plan (Planejar):** Decide se precisa acionar uma ferramenta do catálogo ou se possui dados suficientes para responder.
3. **Act (Agir):** O ambiente de execução invoca a API/função solicitada deterministicamente.
4. **Observe (Observar):** O resultado/retorno bruto da ferramenta é injetado no contexto do modelo.
5. **Score / Refletir:** Avalia se o objetivo foi cumprido ou se é necessária uma nova iteração.

### Travas de Segurança do Runtime
* **Limite de Iterações (`MAX_PASSOS`):** Previne que falhas de ferramenta coloquem o agente em loop infinito.
* **Orçamento de Tokens (`TOKEN_BUDGET`):** Limita a soma de tokens de entrada e saída por execução do agente. Se uma resposta pedir uma ferramenta após atingir o limite, a ferramenta e novas chamadas ao modelo são interrompidas; a chamada já em andamento pode alcançar ou ultrapassar o orçamento.
* **Tratamento de Exceções:** Erros de execução de ferramentas e retornos em formato inválido voltam ao modelo como observações estruturadas (`is_error=True`), permitindo autocorreção de parâmetros. Falhas do provedor são registradas e propagadas explicitamente.

---

## 4. O Padrão de Autonomia Graduada (*Graduated Autonomy*)
Dado o caráter não determinístico dos LLMs, as permissões são organizadas em **Níveis de Confiança (Tiers)**:

| Nível (*Tier*) | Escopo de Ação | Permissões e Regras de Governança |
| :--- | :--- | :--- |
| **T1: Probation (Probatório)** | Leitura / Consulta | Acesso restrito a consultas; escrita e alterações são bloqueadas. |
| **T2: Supervised (Supervisionado)** | Operações de Escrita | Permite escrita de baixo risco; ações mutáveis relevantes exigem aprovação humana (*Human-in-the-Loop*). |
| **T3: Trusted (Confiável)** | Modificação & Execução | Execução autônoma com alertas automáticos de anomalia e monitoramento de desvios. |
| **T4: Autonomous (Autônomo)** | Acesso Total | Acesso autônomo com auditoria e verificação pós-execução. |

* **Regras de Transição:** A promoção para *tiers* superiores exige consistência demonstrada em múltiplas execuções de *benchmarks*. **O rebaixamento é imediato** ao detectar qualquer violação de segurança ou injeção de prompt.

---

## 5. Padrões de Orquestração Multi-Agente (Passo 2 do Estudo)
Quando a complexidade excede a capacidade de um único agente, utilizam-se cinco padrões fundamentais de orquestração:

1. **Sequencial (Pipeline):** Encadeamento linear determinístico onde a saída do Agente A alimenta diretamente o Agente B.
2. **Concorrente (Paralelo):** Múltiplos agentes analisam a mesma entrada em paralelo sob diferentes perspectivas (ex: Arquitetura, Segurança e Qualidade) e um consolidador agrupa as saídas.
3. **Chat em Grupo / *Maker-Checker*:** Discussão colaborativa ou ciclo de criação e validação cruzada entre um especialista criador (*Maker*) e um auditor (*Checker*).
4. **Transferência Dinâmica (*Handoff* / Triagem):** Roteamento progressivo onde o controle total é delegado de um agente para outro à medida que o contexto evolui.
5. **Magêntico / Planejamento Adaptativo:** Um orquestrador central mantém um registro dinâmico de tarefas (*task ledger*) para metas abertas, atribuindo e reordenando subtarefas conforme a execução avança.

### Princípio da Delegação
O orquestrador enxerga a delegação como **apenas mais uma ferramenta** em seu catálogo. Ao delegar, o orquestrador invoca o laço ReAct do sub-agente especialista com um contexto isolado e autocontido, reduzindo drasticamente a janela de contexto necessária e o risco de alucinação.

---

## 6. Caso de Uso de Referência: Esteira de Revisão de Código Corporativa (SDLC)
O cenário prático de aplicação adotado no estudo é a **Esteira de Revisão de Código em CI/CD**:

* **Entrada:** Disparo automatizado por webhook a cada *Pull Request* (PR) aberto ou atualizado.
* **Topologia Multi-Agente:**
  * **Agente Auditor de Arquitetura:** Valida o acoplamento, isolamento de domínio e limites da arquitetura limpa/hexagonal.
  * **Agente Auditor de Qualidade & Clean Code:** Analisa duplicidades, padrões de projeto e injeção de dependências.
  * **Agente Auditor de Segurança & LGPD:** Identifica segredos hardcoded, vulnerabilidades OWASP e exposição de PII em logs.
* **Princípio da Separação de Decisão:** Os agentes geram **apenas achados estruturados** (*Findings*). Eles não possuem permissão de aprovação ou mesclagem (*merge*) no repositório.
* **Quality Gate Determinístico:** Uma função pura e determinística no CI/CD lê a lista unificada de achados e calcula o status do gate (`PASSED`, `WARNING` ou `BLOCKED`).

---

## 7. Próximos Passos do Roteiro de Aprendizado
1. **Consolidação do Passo 1:** Exercitar o laço ReAct com ferramentas locais e tratamento estrito de exceções.
2. **Implementação do Passo 2:** Construir um pipeline sequencial de 2 agentes (*Maker-Checker*) com validação de esquema de entrada e saída.
3. **Evolução para o Passo 3:** Adicionar a camada de autorização determinística externa (*Deny-by-Default*) e *Guardrails* de entrada/saída.
