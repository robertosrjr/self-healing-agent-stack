---
name: api-design-guidance
description: "Use when designing HTTP APIs, request/response contracts, error formats, OpenAPI documentation, and versioning for Python services."
---

# Design de API para Python

Use esta skill quando o projeto passar a expor uma API HTTP. A aplicação atual
é um protótipo local: os contratos Pydantic do Maker-Checker não constituem
endpoints REST, e FastAPI ainda não é uma dependência escolhida.

## Design de recursos

- Use substantivos plurais e métodos HTTP semânticos.
- Defina idempotência, autenticação, autorização, limites, paginação e versionamento
  conforme o caso de uso, não por convenção sem análise.
- Documente schemas, exemplos, erros e mudanças breaking na especificação
  OpenAPI versionada junto ao código.

## Status e erros

Use códigos HTTP conforme o contrato e diferencie erro sintático de regra de
domínio. `400` e `422` podem ser usados para validação conforme framework e
convenção escolhidos; padronize e documente. `500` não deve revelar traceback,
segredos, prompts ou dados rejeitados.

Para uma API JSON, considere o formato Problem Details (RFC 9457), com campos
estáveis como `type`, `title`, `status`, `detail` seguro e `instance`. Erros
por campo podem ser uma extensão documentada; não inclua valores recebidos.

## Pydantic e frameworks

- Reutilize modelos Pydantic de request/response quando forem contratos
  externos adequados; não exponha automaticamente modelos internos.
- FastAPI pode gerar OpenAPI a partir de type hints e modelos Pydantic, se for
  selecionado como framework.
- Em qualquer framework, mantenha validação e lógica de aplicação fora do
  handler/controller e não acople o domínio à camada HTTP.
- Teste contratos com cliente de teste do framework e casos de status, schema,
  autenticação, limites e erros; use servidor real apenas quando necessário.

## Compatibilidade de contrato

- Adições opcionais podem ser compatíveis, mas confirme consumidores e schema
  antes de assumir.
- Alterar/remover campo obrigatório, tipo ou semântica costuma ser breaking.
- Versione endpoint/schema para mudanças incompatíveis e documente depreciação.

## Como responder

1. Confirme se é API pública, interna ou inexistente ainda.
2. Defina request, response, validação, erros, segurança e compatibilidade.
3. Gere exemplos Python apenas para framework escolhido; não assuma FastAPI.
4. Não documente a função local Maker-Checker como endpoint existente.
