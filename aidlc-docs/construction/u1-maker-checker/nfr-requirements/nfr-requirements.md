# Requisitos Não Funcionais — U1 Maker-Checker e Contratos de Schema

## Escopo

Este documento define requisitos para a validação de entradas e saídas do
incremento local R1. O sistema continua sendo um protótipo de aprendizado; os
requisitos abaixo não implicam disponibilidade, segurança operacional ou
prontidão de produção.

## Decisões recebidas

- **Validação:** Pydantic v2.
- **Propriedades extras:** rejeitadas por padrão; qualquer exceção deverá ser
  explicitamente declarada no modelo/contrato.
- **Erros expostos:** código do erro e caminho do campo, sem ecoar o valor
  rejeitado.

## Requisitos

### Determinismo e integridade

1. Cada fronteira de entrada/saída deve ser validada pelo código da aplicação,
   nunca por instrução ao LLM ou autoavaliação do agente.
2. A configuração de modelos deve rejeitar campos extras, a menos que um
   contrato específico os permita de forma explícita.
3. Parsing ou validação malsucedidos devem encerrar o fluxo antes de qualquer
   trabalhador dependente ser invocado.
4. Apenas os enums e transições definidos pelos contratos podem determinar o
   estado do fluxo; ausência de decisão não equivale a aprovação.
5. As mesmas entradas devem produzir o mesmo resultado de validação, sem
   chamadas de rede, relógio ou estado global no validador.

### Tratamento de falhas e privacidade

1. Erros de validação retornados ao chamador devem conter código estável e
   localização/caminho do campo quando disponível.
2. Valores de entrada rejeitados, prompts, logs completos e segredos não devem
   ser incluídos na mensagem de erro por padrão.
3. A exceção de domínio deve distinguir erro de contrato de decisão válida
   `REJECTED` ou `INCONCLUSIVE`.
4. Erros de contrato não podem ser convertidos em defaults, resultado vazio ou
   resposta com aparência de sucesso.
5. O Checker não deve ser invocado se a saída Maker falhar validação.

### Testabilidade e manutenção

1. Contratos devem ser representados por modelos Pydantic tipados e fáceis de
   testar sem dependência de provedores LLM.
2. Testes devem cobrir campos ausentes, tipos incorretos, propriedades extras,
   JSON inválido, enums desconhecidos e resultados aprovados/rejeitados/
   inconclusivos.
3. Dependência e versão principal Pydantic devem ser declaradas no manifesto
   da aplicação quando o código for implementado.
4. A validação deve continuar compatível com Python e com o fluxo de execução
   existente; mudanças não relacionadas ao runtime ReAct ficam fora do escopo.

## Fora do escopo

- Autenticação, autorização externa, PEP/PDP, guardrails de prompt ou de
  conteúdo, redaction abrangente, ingestão CI/CD, sandbox e deploy.
- Metas de latência, throughput ou disponibilidade para serviço de produção;
  o incremento é local e não define SLO de produção.
- Registrar ou persistir dados rejeitados para auditoria. O erro deve ser
  seguro por padrão; necessidade futura de diagnóstico deve usar referência
  protegida e política explícita de retenção.
