---
name: resilience-checker-skill
description: "Use when reviewing or implementing resilience in Python applications, including provider timeouts, retries, idempotency, concurrency limits, rate limiting, caching, and explicit failure handling."
---

# Resiliência em Aplicações Python

Avalie resiliência conforme dependências e carga reais. O protótipo atual tem
chamadas síncronas a provedores LLM e ferramentas locais; ele não é um serviço
distribuído nem tem fila, banco ou cache implantados.

## Workflow

1. Mapeie chamadas de rede, persistência, filas, subprocessos e estado
   compartilhado; diferencie dependências atuais de arquitetura-alvo.
2. Classifique falhas como permanentes, transitórias, timeout, sobrecarga,
   resposta inválida ou execução duplicada.
3. Configure timeouts explícitos no cliente/SDK suportado e teste o limite.
4. Só adicione retry quando operação for segura/idempotente, exceções
   transitórias forem identificáveis e backoff com jitter e limite de tentativas
   estiver definido.
5. Defina comportamento de falha antes de qualquer fallback. Falha de provedor
   ou contrato inválido deve continuar explícita e nunca virar aprovação.
6. Adicione circuit breaker, bulkhead ou rate limiting apenas em fronteiras
   independentes que justifiquem esses mecanismos.
7. Teste timeout, erro, concorrência, repetição e condições de recuperação com
   dependências simuladas; não faça testes de caos sem ambiente e stop
   conditions aprovados.

## Opções Python

- Use timeout/configuração oferecidos pelo SDK cliente existente quando
  confirmados para a versão instalada.
- Para HTTP direto, escolha cliente e timeout dentro da decisão arquitetural;
  não introduza `httpx`, `tenacity` ou biblioteca de circuit breaker sem
  atualizar manifesto e justificar o uso.
- Semáforos/limites de concorrência só ajudam se o processamento for realmente
  concorrente e o escopo do limite estiver definido (processo ou distribuição).
- Cache exige política de chave, validade, invalidação e privacidade dos dados.

## Regras

- Não adicionar retry cego a chamadas de custo variável, mutações ou operações
  não idempotentes.
- Não repetir respostas inválidas do LLM automaticamente para "corrigi-las"
  sem política explícita e orçamento.
- Não usar circuit breaker sem dependência isolável e sinais suficientes.
- Limitar filas, concorrência e tentativas.
- Propagar erros com contexto sem expor segredos, prompts ou payloads pessoais.
- Registrar claramente se controles são locais ao processo ou distribuídos.

## Referência

Consulte [resilience-checker-skill.md](references/resilience-checker-skill.md)
para padrões e testes de falha em Python.
