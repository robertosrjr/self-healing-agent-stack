# Plano de estudo — Passo 1: runtime do agente

## Objetivo

Consolidar a unidade básica do sistema de agentes: um loop ReAct que recebe
uma tarefa, consulta o modelo, executa ferramentas de forma determinística,
devolve os resultados ao modelo e termina com uma resposta ou um estado de
falha explícito.

O foco desta etapa é aprender e testar os controles do runtime. Não é ainda
construir a solução corporativa de revisão de Pull Requests.

## Fluxo de execução

```text
Tarefa
  │
  ▼
Think / Plan ── modelo decide se precisa de ferramenta
  │
  ├── resposta final ──────────────────────────────► conclusão
  │
  └── chamada de ferramenta
        │
        ▼
      Act ───── função Python executada pelo runtime
        │
        ▼
      Observe ─ resultado ou erro estruturado volta ao modelo
        │
        └──────────────────────────► próxima iteração
```

O histórico da conversa cresce ao longo do loop e preserva a resposta completa
do assistente, incluindo chamadas a ferramentas, para manter o protocolo exigido
pelo provedor.

## Controles e comportamento implementados

| Controle | Configuração | Comportamento |
|---|---|---|
| Limite de iterações | `MAX_PASSOS` (padrão: `10`) | Impede que o agente faça um número ilimitado de chamadas ao modelo. Ao esgotar o limite, registra a execução como limitada e retorna uma mensagem explícita. |
| Orçamento de tokens | `TOKEN_BUDGET` (padrão: `20000`) | Soma os tokens de entrada e saída informados pelo provedor durante uma execução. Se o modelo pedir ferramenta depois de o orçamento ser atingido, o runtime não executa a ferramenta, não inicia outra chamada ao modelo, registra o limite e lança `RuntimeError`. |
| Erro de ferramenta | Exceção durante a chamada | Converte a falha em resultado de ferramenta com `is_error=True`, para que o modelo possa observar o erro e tentar corrigir a chamada. |
| Formato de retorno de ferramenta | A ferramenta deve retornar `str` | Um tipo de retorno diferente é tratado como erro de ferramenta e volta ao modelo como resultado estruturado. |
| Erro do provedor | Exceção durante a chamada ao modelo | Registra métricas e falha no histórico/sessão, e propaga a exceção em vez de apresentar uma resposta com aparência de sucesso. |
| Recusa do modelo | `stop_reason == "refusal"` | Registra a execução como recusada e devolve um marcador explícito de recusa. |
| Resposta truncada | `stop_reason == "max_tokens"` | Registra um alerta e marca a resposta como truncada. |
| Observabilidade | Métricas de execução | Registra passos, tokens de entrada e saída e duração. Quando a sessão está habilitada, também grava as etapas e o estado da execução. |

Os limites `MAX_PASSOS` e `TOKEN_BUDGET` devem ser maiores que zero. As
configurações ficam em `application/config.py`; a cópia de referência para
novos ambientes está em `application/.env.example`.

## Precisão e limites do orçamento de tokens

O provedor informa o uso de tokens depois de produzir cada resposta. Por isso,
`TOKEN_BUDGET` é um limite de controle entre iterações, não um teto rígido que
possa cancelar uma requisição já em andamento:

- Se a resposta que alcança o limite pedir uma ferramenta, essa ferramenta não
  será executada.
- Se a resposta que alcança ou ultrapassa o limite já for final, ela é
  devolvida e registrada; não há uma iteração subsequente a interromper.
- A contagem depende dos dados de uso retornados pelo provedor. Quando eles não
  estão disponíveis, o runtime registra zero para o dado ausente.
- O orçamento é por execução de cada agente. Não representa um orçamento
  agregado para todos os agentes de uma orquestração nem um limite monetário.

## Organização da implementação

- `application/agente.py`: loop ReAct, invocação de ferramentas, tratamento
  dos estados finais, métricas e limites de execução.
- `application/config.py`: valores padrão e leitura das configurações.
- `application/.env.example`: exemplo de configuração local, sem credenciais.
- `application/tests/test_openrouter_client.py`: testes do protocolo OpenRouter
  e dos controles do loop.
- `application/tests/test_execucao_historico.py`: persistência e resumo do
  histórico de execuções.

## Critérios de conclusão do Passo 1

- [x] O runtime executa o ciclo de chamada ao modelo e execução de ferramentas.
- [x] O número máximo de iterações é limitado por configuração.
- [x] O consumo informado de tokens é acumulado e comparado a um orçamento.
- [x] Erros de ferramenta voltam ao modelo como observações com `is_error`.
- [x] Falhas do provedor são registradas e propagadas.
- [x] Recusas, truncamentos e esgotamento dos limites têm tratamento explícito.
- [x] Os principais comportamentos estão cobertos por testes automatizados.

## Validação

Executar a suíte a partir da pasta `application`:

```powershell
python -m pytest tests -q
```

Na validação desta etapa, a suíte terminou com **16 testes aprovados**.

## Fora do escopo desta etapa

O Passo 1 é uma implementação didática do runtime; não deve ser confundido com
um ambiente pronto para produção. Permanecem para etapas posteriores, entre
outros:

- isolamento de processos, containers ou microVMs entre usuários e tarefas;
- checkpoints duráveis e retomada de execuções interrompidas;
- orçamento agregado de tokens/custo para um fluxo com vários agentes;
- autorização externa de ferramentas com política *deny-by-default*;
- guardrails de entrada e saída;
- integração com webhooks, diffs de Pull Requests e CI/CD.

## Próxima etapa do roteiro

Com o loop e seus limites exercitados, o próximo passo é construir um pipeline
Maker-Checker pequeno e determinístico: um agente produz um resultado, outro o
confere, e o runtime valida os contratos de entrada e saída por esquema. A
camada de autorização e os guardrails ficam para a etapa seguinte, antes da
aplicação no fluxo corporativo de revisão de código.
