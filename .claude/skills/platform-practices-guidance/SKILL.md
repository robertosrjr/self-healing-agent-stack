---
name: platform-practices-guidance
description: "Use when preparing Python applications for cloud/platform deployment, applying Twelve-Factor principles, or choosing synchronous versus asynchronous I/O."
---

# Práticas de Plataforma para Python

Use os princípios Twelve-Factor e Reactive como heurísticas, adaptados à stack
Python e ao tamanho real do serviço. O protótipo atual não possui servidor web,
deployment, health endpoints ou infraestrutura de produção.

## Princípios aplicáveis

| Princípio | Aplicação Python |
|---|---|
| Codebase | Um repositório versionado e configuração explícita por ambiente. |
| Dependências | Declarar dependências em `requirements.txt`; separar ferramentas de desenvolvimento quando útil. |
| Configuração | Ler configuração do ambiente; manter `.env` apenas para desenvolvimento local e fora do git. |
| Backing services | Tratar APIs, bancos e filas como dependências substituíveis por configuração/adapters. |
| Build/release/run | Separar instalação, validação/testes, empacotamento e execução quando houver release. |
| Processos | Tornar workers descartáveis; mover estado durável para backing service somente quando necessário. |
| Port binding | Aplicável quando existir servidor HTTP selecionado. |
| Concorrência | Escalar processo/worker conforme perfil; medir antes de adicionar threads, processos ou async. |
| Descartabilidade | Encerrar processos graciosamente se houver servidor ou worker de longa duração. |
| Paridade de ambientes | Manter versões e dependências reproduzíveis; usar serviços reais em integração somente quando existirem. |
| Logs | Emitir para stdout/stderr com redaction/minimização, deixando coleta e retenção ao ambiente. |
| Tarefas administrativas | Scripts/CLI isolados, explícitos e seguros para repetição quando aplicável. |

## Síncrono ou assíncrono

- O código atual usa chamadas síncronas. Preserve esse modelo enquanto carga,
  SDKs e requisitos não justificarem concorrência.
- `asyncio` é adequado para muitas operações I/O concorrentes com suporte async
  em toda a cadeia. Não misture chamadas bloqueantes longas no event loop.
- Thread/process pools ou workers podem ser apropriados para I/O bloqueante ou
  CPU-bound, respectivamente; defina limites e propagação de contexto.
- Não adote um modelo reativo apenas por tendência nem acrescente complexidade
  sem benchmark e requisito de concorrência.

## Operacionalização futura

Se um serviço HTTP for introduzido, escolha framework explicitamente; defina
health/readiness, timeouts, shutdown, limites de recursos, autenticação,
telemetria e gestão de segredos. FastAPI/ASGI ou outro framework são opções,
não dependências atuais do repositório.

## Como responder

1. Identifique o que existe hoje e o destino pretendido.
2. Priorize configuração externa, dependências declaradas e comportamento de
   processo adequado ao escopo.
3. Recomende síncrono/assíncrono com base em carga, SDK e medições.
4. Não gere configuração Docker/Kubernetes nem declare prontidão operacional
   sem solicitação e implementação correspondente.
