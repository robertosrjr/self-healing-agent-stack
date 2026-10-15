# Plano de NFR Design — U1 Maker-Checker e Contratos de Schema

## Objetivo

Traduzir os NFR aprovados em padrões e componentes lógicos para o incremento R1,
sem incluir infraestrutura de produção.

## Checklist

- [x] Aplicar validação por Pydantic v2 em todas as fronteiras de dados
- [x] Definir comportamento fail-closed e normalização segura de erros
- [x] Separar coordenação de agentes da validação determinística
- [x] Definir testabilidade sem provedores externos
- [x] Mapear componentes e fluxo lógico
- [x] Confirmar que infraestrutura externa não é necessária no R1

## Perguntas

Não há decisões pendentes que alterem o padrão lógico: estratégia de schema,
política de campos extras e formato seguro de erro foram decididos e aprovados
na etapa NFR Requirements.

## Artefatos

- `aidlc-docs/construction/u1-maker-checker/nfr-design/nfr-design-patterns.md`
- `aidlc-docs/construction/u1-maker-checker/nfr-design/logical-components.md`
