# Resiliência em serviços Python

Esta referência complementa a skill principal com padrões agnósticos de
biblioteca. Adote somente os mecanismos justificados por uma dependência real.

## Limites de timeout

Configure timeout explícito para cada chamada de rede, incluindo chamadas a
provedores de modelos. Use a opção suportada pela versão instalada do SDK e
teste timeout e propagação de falha. Um timeout por chamada não substitui um
limite total para a execução do caso de uso.

## Retry

Retry é apropriado somente quando:

- a falha é transitória e identificável;
- a operação é segura para repetição ou possui idempotency key;
- tentativas totais, deadline, backoff exponencial, jitter e exceções elegíveis
  são limitados e documentados;
- custo e rate limits do provedor são considerados.

Não repita erros de schema, autenticação, validação ou outras falhas permanentes.
Não repita automaticamente a geração de saída inválida para forçar uma resposta
válida. Se `tenacity` for selecionada, declarar a dependência e configurar
política por operação; não aplicar decorators genéricos em toda chamada.

## Circuit breaker e concorrência

Um circuit breaker precisa de dependência remota que falhe independentemente,
volume suficiente para medir falhas e política explícita ao abrir. Respostas
abertas devem ser falhas explícitas, não resultados aprovados.

Use semáforos, limites de worker ou filas limitadas somente quando houver
concorrência real. Documente se o limite é por processo ou global. Não introduza
um pool ilimitado que apenas mova o problema de saturação.

## Rate limiting e caching

- Limite chamadas quando quotas, custo ou abuso justificarem; determine se o
  controle deve ser distribuído entre processos.
- Cache precisa de chave estável, TTL, invalidação e análise de conteúdo
  sensível. Não armazene prompts/respostas sem necessidade e política de
  retenção.

## Invariantes de falha

- Nenhuma falha de rede, timeout ou erro de worker vira sucesso ou aprovação.
- Não faça retry de operações mutáveis sem idempotência comprovada.
- Propague a causa ou traduza-a em exceção tipada sem incluir segredos.
- Métricas e logs de falha não devem conter payloads integrais.
- Testes de caos só podem ocorrer em ambiente autorizado, limitado e com
  condição de parada/rollback definida.

## Testes direcionados

Teste worker indisponível, timeout, saída inválida, rate limit, repetição
duplicada e concorrência acima do limite por meio de fakes ou servidores
controlados. Mantenha os testes unitários offline; reserve testes de integração
para adapters reais.
