# Plano de NFR Requirements — U1 Maker-Checker e Contratos de Schema

## Objetivo

Definir requisitos não funcionais e abordagem técnica para validar contratos
de entrada e saída no incremento local R1. A validação deve ser determinística,
testável e falhar fechado. Não inclui controle de acesso externo ou guardrails,
que são incrementos posteriores.

## Checklist

- [x] Revisar functional design e fronteiras de validação da U1
- [x] Identificar decisões de tecnologia, robustez e privacidade que precisam de entrada do usuário
- [x] Coletar respostas das perguntas abaixo
- [x] Consolidar requisitos NFR e decisão de tecnologia
- [x] Validar compatibilidade conceitual da escolha com a aplicação Python existente; instalação fica para Code Generation

## Q1: Qual estratégia/biblioteca deve validar os schemas Python?

A. Pydantic v2 — modelos tipados e validação integrada; adiciona dependência. (Recomendado)  
B. `jsonschema` — validação por JSON Schema padrão; adiciona dependência.  
C. Validador mínimo próprio usando biblioteca padrão — sem dependência, mas com escopo de schema limitado e lógica de validação mantida pelo projeto.  
D. Outra (descreva após `[Answer]:`)

[Answer]: A — Pydantic v2

## Q2: Como tratar propriedades não declaradas no schema?

A. Rejeitar propriedades extras por padrão; cada contrato pode permitir explicitamente as exceções necessárias. (Recomendado)  
B. Ignorar propriedades extras durante a validação.  
C. Preservar propriedades extras na saída validada, sem usá-las para decisões.  
D. Outra (descreva após `[Answer]:`)

[Answer]: A — rejeitar propriedades extras por padrão

## Q3: Que detalhe deve aparecer em erros de validação retornados ao chamador?

A. Código do erro e caminho do campo, sem incluir o valor rejeitado. (Recomendado)  
B. Mensagem genérica sem indicar o campo inválido.  
C. Código, caminho e valor recebido para facilitar depuração.  
D. Outra (descreva após `[Answer]:`)

[Answer]: A — código do erro e caminho do campo, sem incluir o valor rejeitado

## Restrições já definidas

- Erros de validação não podem retornar sucesso nem uma resposta aprovada.
- O Checker não é invocado se a saída do Maker for inválida.
- Nenhum valor rejeitado ou conteúdo sensível deve ser registrado por padrão.
- A biblioteca escolhida não pode mudar a semântica funcional definida nos
  artefatos de Functional Design.
- A decisão deve ser verificada por testes sem chamadas reais a provedores LLM.
