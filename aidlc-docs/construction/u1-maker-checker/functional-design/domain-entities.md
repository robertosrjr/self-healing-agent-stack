# Entidades de Domínio — U1 Maker-Checker

Os esquemas abaixo são contratos lógicos independentes da biblioteca Python a
ser selecionada na etapa NFR Requirements. Campos são tipados e limites de
tamanho serão definidos junto à implementação.

## `MakerCheckerRequest`

| Campo | Tipo lógico | Obrigatório | Regra |
|---|---|---:|---|
| `request_id` | string | Sim | Identificador não vazio para correlação. |
| `task` | string | Sim | Instrução não vazia e limitada em tamanho. |
| `context` | object | Sim | Dados estruturados aceitos pelo caso de uso. |

## `MakerResult`

| Campo | Tipo lógico | Obrigatório | Regra |
|---|---|---:|---|
| `status` | enum | Sim | `COMPLETED` ou `INCONCLUSIVE`. |
| `payload` | object | Sim | Resultado de domínio estruturado. |
| `evidence` | array[string] | Sim | Evidências; pode ser vazio somente quando o contrato de negócio permitir. |

Uma saída Maker inconclusiva pode ser passada ao Checker somente se o caso de
uso assim determinar; no R1, `status=INCONCLUSIVE` encerra a execução com
resultado inconclusivo e não dispara aprovação.

## `CheckerInput`

| Campo | Tipo lógico | Obrigatório | Regra |
|---|---|---:|---|
| `request` | `MakerCheckerRequest` | Sim | Request original já validado. |
| `maker_result` | `MakerResult` | Sim | Resultado Maker validado. |

## `CheckerResult`

| Campo | Tipo lógico | Obrigatório | Regra |
|---|---|---:|---|
| `decision` | enum | Sim | `APPROVED`, `REJECTED` ou `INCONCLUSIVE`. |
| `findings` | array[string] | Sim | Achados que fundamentam a decisão. |
| `rationale` | string | Sim | Justificativa não vazia e limitada em tamanho. |

## `MakerCheckerResponse`

| Campo | Tipo lógico | Obrigatório | Regra |
|---|---|---:|---|
| `request_id` | string | Sim | Ecoa o identificador do request validado. |
| `status` | enum | Sim | `APPROVED`, `REJECTED` ou `INCONCLUSIVE`. |
| `maker_result` | `MakerResult` | Sim | Resultado validado do Maker. |
| `checker_result` | `CheckerResult` | Sim | Decisão validada do Checker. |

`status` deve corresponder à decisão do Checker. Erros de parsing/schema e
falhas operacionais são exceções explícitas e não são serializados como uma
resposta válida com status de sucesso.
