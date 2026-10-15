# Decisões de Tecnologia — U1 Maker-Checker

## ADR curto: validação de contratos

### Status

Aceito para o incremento R1, sujeito à aprovação dos artefatos NFR.

### Decisão

Usar **Pydantic v2** para representar e validar os contratos de entrada,
resultado do Maker, entrada do Checker, resultado do Checker e resposta final.
Configurar cada modelo para rejeitar atributos não declarados por padrão.

Erros apresentados pela camada de aplicação devem ser normalizados para incluir
um código estável e o caminho do campo quando disponível, sem incluir o valor
rejeitado. A camada de domínio deve diferenciar falha de parsing/schema de uma
decisão válida do Checker.

### Contexto e alternativas

- `jsonschema`: oferece aderência direta a JSON Schema e é alternativa válida
  se interoperabilidade de schemas externos passar a ser requisito.
- Validador próprio com biblioteca padrão: evita dependência, mas aumentaria
  código de validação e risco de comportamento incompleto/inconsistente.

Pydantic v2 foi selecionado por se adequar aos modelos tipados internos do
projeto Python e fornecer validação declarativa com erros estruturados. A
dependência deve ser adicionada ao manifesto da aplicação junto à implementação,
e sua versão deve ser limitada a uma faixa v2 compatível com o ambiente
suportado pelo projeto. Instalação/restore ocorre na etapa de Code Generation,
não durante o planejamento.

### Consequências e trade-offs

- Modelos explícitos melhoram legibilidade, validação e cobertura de testes.
- Nova dependência externa requer atualização de `application/requirements.txt`
  e testes de compatibilidade.
- Modelos Python não equivalem automaticamente a um contrato JSON Schema
  publicado; exportação/interoperabilidade poderá ser definida numa etapa
  posterior.
- `extra="forbid"` pode revelar campos adicionais fornecidos por modelos;
  isso é intencionalmente fail-closed. Exceções precisam ser explícitas e
  justificadas por contrato.
- Mensagens detalhadas nativas da biblioteca não devem ser retornadas sem
  normalização, pois podem carregar valores de entrada.

## Configuração técnica prevista

| Item | Decisão |
|---|---|
| Runtime | Python, mantendo a estrutura atual em `application/` |
| Validação | Pydantic v2 |
| Campos extras | Rejeitados por padrão |
| Erro externo | Código e caminho; sem valor rejeitado |
| Testes | pytest existente; casos de schema isolados de chamadas de rede |
| Manifesto | Adicionar dependência durante a implementação, após aprovação |

## Critérios de aceitação técnica

- Modelos de request/response validam tipos e campos obrigatórios.
- Campos adicionais são rejeitados.
- O payload inválido impede invocação do próximo agente.
- Respostas de Checker limitam decisão ao enum previsto.
- Erros normalizados não contêm valores inválidos recebidos.
- Testes de sucesso, rejeição, inconclusão e falha de contrato passam.
