# Geração de Código — U1 Maker-Checker

## Escopo implementado

- Contratos Pydantic estritos para request, resultado do Maker, entrada/resultado
  do Checker e resposta final.
- Rejeição de campos extras, tipos incompatíveis, conteúdo não JSON e payloads
  acima dos limites definidos.
- Erros de contrato expõem código e caminhos, sem ecoar os valores rejeitados.
- Serviço sequencial com workers injetáveis para testes determinísticos.
- Saída inválida do Maker impede a chamada ao Checker; saída Maker inconclusiva
  termina sem invocar o Checker.
- Decisão do Checker determina o estado final. Agentes Maker e Checker não ficam
  disponíveis na delegação genérica do orquestrador.
- Agentes Maker e Checker sem ferramentas; este incremento não concede
  autorização nem capacidade de mutação.

## Arquivos de aplicação

- `application/contratos_maker_checker.py` — modelos, limites e validação.
- `application/maker_checker.py` — coordenação do fluxo e integração com workers.
- `application/especialistas.py` — definições dos agentes Maker e Checker.
- `application/orquestrador.py` — exposição da entrada `executar_maker_checker`.
- `application/requirements.txt` — dependência Pydantic v2.
- `application/tests/test_maker_checker.py` — testes de contrato, decisões,
  falhas e bloqueio de delegação direta.

## Validação

Na pasta `application`, `python -m compileall -q .` passou e
`python -m pytest tests -q` aprovou **29 testes**. A execução focada de
`python -m pytest tests/test_maker_checker.py -q` aprovou **13 testes**.
Consulte o [resumo de Build e Test](../build-and-test/build-and-test-summary.md).

## Limites deste incremento

O fluxo é local e didático. Não implementa webhook, acesso ao repositório,
aplicação de patches, autorização externa, guardrails completos, sandbox,
auditoria imutável, gates de CI/CD ou implantação.
