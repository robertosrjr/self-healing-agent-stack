# Roteiro de observabilidade para Python

Use este roteiro para revisar a instrumentação existente e desenhar incrementos
futuros. Uma aplicação local sem serviço persistente não precisa implementar
Golden Signals de produção.

## 1. Inventário

- Bibliotecas de logs, métricas, traces e exporters declaradas.
- Chamadas a `logging`, `print`, SDKs externos, filas, banco e subprocessos.
- Identificadores de execução disponíveis e dados incluídos nos eventos.
- Caminhos de falha e logs de exceção.

Não instale OpenTelemetry ou stack de métricas só para preencher uma checklist.
Registre a decisão e o requisito que cada exporter atende.

## 2. Golden Signals

Para serviço que recebe carga, medir conforme aplicável:

| Sinal | Exemplo |
|---|---|
| Latência | Histograma de duração por operação estável |
| Tráfego | Contador de operações concluídas/iniciadas |
| Erros | Contador por classe/resultado seguro |
| Saturação | Concorrência ativa, fila delimitada ou recurso utilizado |

Defina SLOs e alertas apenas com objetivo, janela e orçamento acordados.
Métricas de desenvolvimento não são evidência de prontidão de produção.

## 3. Correlação

- Correlacione uma execução com request/event ID não sensível.
- Em arquitetura distribuída, propague trace context W3C em fronteiras HTTP e
  mensagens e inclua trace/span ID em logs quando disponível.
- Não use trace IDs, IDs de request ou nomes de usuário como labels de métricas.
- Não atribua trace distribuído ao protótipo enquanto ele roda localmente sem
  propagação entre serviços.

## 4. Privacidade e cardinalidade

- Não registre prompts completos, respostas LLM, logs de CI, diffs, segredos ou
  PII sem finalidade e proteção explicitamente aprovadas.
- Prefira metadados de baixo risco, operação, duração e categoria de erro.
- Labels devem ser de baixa cardinalidade: sem IDs, emails, URLs dinâmicas ou
  conteúdo de payload.
- Defina amostragem, acesso e retenção para telemetria operacional.

## 5. Aplicação ao repositório atual

O R1 é uma execução local Python sem endpoints HTTP, exporters, armazenamento
operacional ou SLOs. Existem saídas de console no protótipo, mas isso não é
log estruturado nem trilha de auditoria imutável. Antes de integrar repositório,
webhook ou CI/CD, especifique campos seguros, retenção, controles de acesso,
correlação e evidências esperadas.
