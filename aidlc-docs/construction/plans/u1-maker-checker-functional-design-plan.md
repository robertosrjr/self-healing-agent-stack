# Plano de Functional Design — U1 Maker-Checker e Contratos de Schema

## Objetivo

Definir o comportamento de domínio para o incremento R1: coordenação sequencial
Maker-Checker com validação de entradas e saídas estruturadas no runtime local.
O escopo não inclui webhook, mutação de repositório, autorização externa ou
guardrails.

## Checklist

- [x] Definir fronteiras e fluxo Maker -> validação -> Checker -> validação
- [x] Definir estados possíveis e distinção entre rejeição válida e erro
- [x] Definir entidades lógicas e seus campos obrigatórios
- [x] Definir comportamento para JSON inválido, schema inválido e resultado inconclusivo
- [x] Mapear critérios de aceitação para testes
- [x] Confirmar que a decisão de aprovação é validada deterministicamente

## Decisões funcionais

- Validar a entrada antes de invocar o Maker.
- Validar a saída do Maker antes de encaminhá-la ao Checker.
- Não invocar o Checker se a saída do Maker for inválida.
- Validar a saída do Checker e aceitar somente decisões enumeradas.
- `APPROVED`, `REJECTED` e `INCONCLUSIVE` são resultados de domínio válidos;
  somente `APPROVED` permite que o fluxo retorne status aprovado.
- Falha de parsing/schema é erro explícito e não é convertida em resposta de
  sucesso nem seguida por retry automático nesta unidade.
- Cada invocação do fluxo tem um identificador de execução para correlação
  dentro da resposta; persistência durável/auditoria externa não faz parte do
  escopo.

## Fora do escopo

- Escolha da biblioteca Python de validação de schema (será decidida na etapa
  NFR Requirements).
- Ingestão CI/CD, patch, git worktree, sandbox, policy service, guardrails,
  armazenamento durável ou deploy.

## Artefatos

- `aidlc-docs/construction/u1-maker-checker/functional-design/business-logic-model.md`
- `aidlc-docs/construction/u1-maker-checker/functional-design/business-rules.md`
- `aidlc-docs/construction/u1-maker-checker/functional-design/domain-entities.md`
