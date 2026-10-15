# Componentes Lógicos — U1 Maker-Checker

## Componentes

| Componente | Tipo | Responsabilidade | Dependências |
|---|---|---|---|
| `MakerCheckerService` | Aplicação | Validar ordem, encadear workers e controlar resultado final. | `ContractValidator`, portas/adaptadores Maker e Checker |
| `ContractValidator` | Domínio/aplicação determinística | Fazer parsing JSON, validar modelos e normalizar erros sem valores de entrada. | Pydantic v2 |
| `MakerWorker` | Porta/adaptador de execução | Receber tarefa estruturada e retornar texto produzido pelo agente Maker. | Runtime `Agente` existente |
| `CheckerWorker` | Porta/adaptador de execução | Receber `CheckerInput` validado e retornar parecer textual do Checker. | Runtime `Agente` existente |
| Modelos de contrato | Domínio | Representar request, resultados Maker/Checker e resposta. | Pydantic v2 |

## Fluxo lógico

```text
Chamador
  -> MakerCheckerService
  -> ContractValidator: request -> MakerCheckerRequest
  -> MakerWorker: request validado -> texto
  -> ContractValidator: texto -> MakerResult
  -> CheckerWorker: CheckerInput validado -> texto
  -> ContractValidator: texto -> CheckerResult
  -> MakerCheckerService: estado consistente
  -> ContractValidator: MakerCheckerResponse
  -> Chamador
```

Cada falha de contrato interrompe o caminho naquele ponto. Falhas de worker
propagam como falhas operacionais; não são recodificadas como parecer de
domínio.

## Implantação no R1

Todos os componentes executam no mesmo processo Python do protótipo em
`application/`. Não são necessários API gateway, fila, banco de dados,
container de sandbox ou serviços cloud nesta unidade. Pydantic v2 será
declarado como dependência da aplicação ao iniciar Code Generation.

## Fronteiras e restrições

- O validador é determinístico e não acessa rede, filesystem ou provedor LLM.
- Workers não recebem autoridade de escrita nem ferramentas de alteração de
  repositório.
- O serviço só retorna `APPROVED` quando a decisão estruturada validada do
  Checker for explicitamente `APPROVED`.
- Logs desta unidade não registram valores rejeitados nem conteúdo integral
  fornecido ao modelo.
- Persistência de auditoria e métricas específicas para Maker-Checker não são
  adicionadas neste incremento, salvo suporte já existente sem mudança de
  comportamento.
