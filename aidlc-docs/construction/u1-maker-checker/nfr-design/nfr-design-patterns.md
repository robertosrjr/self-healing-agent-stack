# Padrões de NFR Design — U1 Maker-Checker

## 1. Validação na fronteira

Validar dados imediatamente ao entrar ou sair de cada componente:

1. `MakerCheckerRequest` antes de invocar Maker;
2. saída textual do Maker: parsing JSON seguido de validação como `MakerResult`;
3. `CheckerInput` criado apenas com dados validados;
4. saída textual do Checker: parsing JSON seguido de validação como
   `CheckerResult`;
5. `MakerCheckerResponse` validado antes de ser retornado ao chamador.

Nenhum objeto cru de modelo é usado como entrada de decisão. A saída validada
é representada pelos modelos Pydantic; a aplicação não depende de `dict.get`
com defaults permissivos para campos decisórios.

## 2. Fail-closed

- Usar configuração comum de modelo com `extra="forbid"`; permitir exceções
  somente quando um contrato documentado exigir campos extras.
- Exigir todos os campos necessários e validar tipos/enums sem coerção que
  altere silenciosamente o sentido de decisões.
- Se parsing ou validação do Maker falhar, encerrar sem chamar Checker.
- Se parsing ou validação do Checker falhar, não construir resposta aprovada.
- Uma decisão de domínio válida `REJECTED` ou `INCONCLUSIVE` é retornada como
  tal; não é convertida em erro de schema nem em aprovação.
- Não repetir automaticamente chamadas para “consertar” uma saída inválida.

## 3. Normalização de erros e minimização

Capturar erros de validação somente no limite do validador e convertê-los para
uma exceção de aplicação com código estável e caminhos de campo. Não expor
`input`, valores recebidos, prompt integral, traceback de provedor ou conteúdo
rejeitado. Não adicionar catch abrangente fora desse limite: falhas de provedor
e programação continuam explícitas e propagadas conforme os padrões do projeto.

## 4. Separação de responsabilidades

- `MakerCheckerService` controla sequência e transições.
- Adaptadores de worker executam os agentes já existentes e retornam texto.
- `ContractValidator` é a única fronteira que parseia/valida respostas de
  trabalhadores para contratos tipados.
- Modelos de domínio não invocam LLMs, ferramentas, filesystem ou rede.
- O Checker recebe contexto estruturado já validado, sem o raciocínio privado
  do Maker.

## 5. Testabilidade

- Injetar ou receber funções de worker na composição do serviço para testes
  determinísticos; produção continua usando os agentes configurados.
- Testar a validação diretamente com entradas em memória.
- Testar a orquestração com workers fake e contadores de invocação.
- Assegurar que testes de erro confirmem que Checker não foi chamado após
  saída Maker inválida.
- Confirmar que mensagens externas não contêm valores rejeitados.
- Não fazer chamadas reais a provedores LLM na suíte unitária.

## 6. Limites do padrão

Esses controles asseguram consistência dos contratos, não correção semântica
das respostas do modelo. Eles não implementam autenticação, autorização,
guardrails contra prompt injection, sandbox ou validação de patch.
