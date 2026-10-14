# Serviços de Orquestração

## `SelfHealingService`
**Responsabilidade:** centralizar o ciclo completo de auto-remediação.  
**Fluxo principal:**
1. receber evento de falha;
2. diagnosticar a causa;
3. propor correção;
4. validar em ambiente isolado;
5. avaliar gates;
6. promover ou bloquear o avanço;
7. registrar a decisão e evidências.

## `DiagnosticService`
**Responsabilidade:** interpretar logs, contexto de repositório e falha operacional.  
**Saída esperada:** um diagnóstico estruturado incluindo severidade, achados e evidências.

## `PatchService`
**Responsabilidade:** transformar uma análise de falha em uma correção focada e revisável.  
**Saída esperada:** patch proposto com escopo limitado e justificativa de causa raiz.

## `ValidationService`
**Responsabilidade:** executar o ciclo de regressão e consolidar resultados.  
**Saída esperada:** relatório de validade do patch e status por ambiente.

## `PolicyService`
**Responsabilidade:** encapsular regras de segurança, autorização e gate de promoção.  
**Saída esperada:** decisão determinística de avanço ou bloqueio.

## `AuditService`
**Responsabilidade:** garantir observabilidade e rastreabilidade operacional.  
**Saída esperada:** trilha completa com todos os eventos relevantes.

## Padrão de comunicação

- Serviços de IA e análise produzem artefatos estruturados em dicionários ou objetos JSON.
- Serviços determinísticos recebem esses artefatos e aplicam regras de promoção, autorização e validação.
- O `SelfHealingService` funciona como ponto de composição para o ciclo completo, preservando o papel do control plane fora do modelo.
