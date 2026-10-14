# Mapa de Histórias por Unidade

## U1 — Maker-Checker e Contratos de Schema
- US-07: validar contratos de entrada e saída entre Maker e Checker

## U2 — Ingressão e Diagnóstico de Falhas
- US-01: receber e classificar falhas de pipeline
- US-02: diagnosticar causa raiz a partir de logs e contexto

## U3 — Proposta de Correção e Escopo
- US-03: propor correção mínima e focada

## U4 — Validação, Gate e Promoção
- US-04: validar correção com regressão
- US-05: aplicar gates e aprovação para produção
- US-06: trilha de auditoria final do ciclo completo

## Verificação de cobertura

Todas as histórias estão mapeadas para uma unidade principal, e a prioridade foi organizada em ordem de dependência de execução:

1. contratos de agente (R1 / U1),
2. diagnóstico e contexto (U2),
3. patch e justificativa (U3),
4. validação, gates, promoção e auditoria (U4).

Esse sequenciamento minimiza retrabalho e estabelece uma base de entrega incremental.
