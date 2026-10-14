# Métodos dos Componentes

## Convenção

Os métodos abaixo representam a superfície pública de alto nível. A lógica detalhada de negócio ficará no estágio de Functional Design e nos passos de implementação.

## `RuntimeOrchestrator`

- `executar_fluxo(pergunta: str) -> str`
  - Executa o fluxo principal do protótipo e devolve a resposta final.
- `delegar_tarefa(agente: str, tarefa: str) -> str`
  - Encaminha a tarefa para um especialista ou worker.
- `obter_resumo_execucao() -> dict`
  - Retorna métricas, histórico e estado da sessão.

## Componentes do incremento atual — R1

### `MakerCheckerService`
- `executar(entrada: dict) -> dict`
  - Valida a entrada, invoca o Maker, valida sua saída, invoca o Checker e
    valida a decisão estruturada antes de devolver sucesso.

### `ContractValidator`
- `validar(dados: object, schema: dict) -> dict`
  - Retorna dados validados ou falha explícita com erros de validação.

## `PipelineEventIngress`

- `receber_evento(evento: dict) -> dict`
  - Recebe o payload bruto do pipeline e retorna o evento normalizado.
- `validar_payload(evento: dict) -> bool`
  - Verifica presença dos campos obrigatórios e estrutura mínima do evento.

## `FailureAnalyzer`

- `analisar(erro: str, contexto_repo: dict) -> dict`
  - Gera diagnóstico com causa provável, evidência, severidade e localização.
- `classificar_falha(logs: str) -> dict`
  - Extrai e categoriza os tipos de erro mais prováveis.

## `PatchPlanner`

- `propor_patch(falha: dict) -> dict`
  - Produz proposta de mudança focada e justificada.
- `validar_escopo(patch: dict) -> bool`
  - Garante que a mudança está dentro do escopo permitido.

## `RegressionTester`

- `executar_validacao(patch: dict, ambiente: str) -> dict`
  - Executa testes de regressão e retorna status, evidência e falhas.
- `coletar_resultados() -> dict`
  - Aggrega e consolida os resultados do ambiente de execução.

## `QualityGateEvaluator`

- `avaliar(resultado_teste: dict, contexto: dict) -> dict`
  - Decide se o resultado do ambiente atende ao critério para promoção.
- `aplicar_regra(gate: str, resultado: dict) -> bool`
  - Emprega regra determinística específica para um ambiente.

## `PromotionManager`

- `promover(decisao: dict) -> dict`
  - Executa o estado de promoção por ambiente.
- `solicitar_aprovacao_producao() -> dict`
  - Solicita aprovação humana explícita para produção, obrigatória além dos gates.

## `AuditTrail`

- `registrar(evento: str, dados: dict) -> dict`
  - Insere o evento no histórico de auditoria.
- `consultar(evento_id: str) -> dict`
  - Recupera o registro relacionado por identificador.

## Tipos esperados de retorno

- `dict` com `status`, `dados`, `evidencias`, `erros` e `metadados` quando necessário.
- `bool` para regras determinísticas e validações pontuais.
- `str` apenas quando a saída final do runtime for apresentada ao usuário.
