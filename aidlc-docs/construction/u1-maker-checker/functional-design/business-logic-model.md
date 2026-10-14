# Modelo de Lógica de Negócio — U1 Maker-Checker

## Objetivo

Orquestrar dois trabalhadores com responsabilidades distintas e validar cada
fronteira de dados com regras determinísticas. O Maker produz uma análise
estruturada; o Checker avalia essa análise e emite uma decisão enumerada. O
orquestrador não infere aprovação a partir de texto livre.

## Fluxo

1. Receber `MakerCheckerRequest`.
2. Validar os campos obrigatórios e limites do request.
3. Invocar o Maker uma vez com a tarefa e contexto validados.
4. Interpretar e validar a resposta como `MakerResult`.
5. Se a resposta não puder ser interpretada ou violar o contrato, encerrar com
   erro explícito; não invocar o Checker.
6. Construir `CheckerInput` somente com o request validado e o `MakerResult`
   validado.
7. Invocar o Checker uma vez e interpretar sua resposta como `CheckerResult`.
8. Se a resposta do Checker for inválida, encerrar com erro explícito.
9. Retornar resultado estruturado. Somente decisão `APPROVED` resulta em
   `status=APPROVED`; `REJECTED` e `INCONCLUSIVE` são resultados válidos, mas
   bloqueados.

## Responsabilidades

### Orquestrador

- Controla a ordem das etapas.
- Não permite que texto do modelo altere o contrato ou o fluxo.
- Não retorna sucesso antes de concluir as validações.
- Propaga falhas de validação sem substituir a saída inválida por valores
  default ou respostas vazias.

### Maker

- Produz conteúdo de domínio estruturado no contrato definido.
- Não decide se sua própria saída está aprovada.
- Não controla ferramentas, permissões ou transições externas.

### Checker

- Avalia o resultado validado do Maker usando a tarefa e contexto necessários.
- Emite uma decisão estruturada e findings associados.
- Não altera o conteúdo original do Maker; findings devem identificar a
  justificativa de rejeição ou incerteza.

### Validador de contratos

- Valida entrada, saída Maker e saída Checker.
- Retorna dados somente após parsing e validação completos.
- Diferencia falha de formato/schema de uma decisão de domínio `REJECTED` ou
  `INCONCLUSIVE`.

## Estados de resultado

| Estado | Significado | Permite prosseguir |
|---|---|---|
| `APPROVED` | Saída Maker válida e Checker aprovou. | Sim, apenas como resultado do R1. |
| `REJECTED` | Checker válido rejeitou a proposta. | Não. |
| `INCONCLUSIVE` | Checker válido não encontrou evidência suficiente. | Não. |
| Erro de contrato | Parsing, tipo, campo ou enum inválido. | Não; erro explícito. |
| Erro operacional | Worker/provedor falhou ou excedeu limite. | Não; erro explícito. |

## Invariantes

- Checker nunca recebe saída Maker inválida.
- Status aprovado nunca é derivado de texto livre ou campo ausente.
- Erros operacionais e de contrato não se transformam em `APPROVED`,
  `REJECTED` ou outro resultado de domínio artificial.
- A unidade não altera arquivos do repositório nem promove ambientes.
