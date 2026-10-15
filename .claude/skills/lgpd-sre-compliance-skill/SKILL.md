---
name: lgpd-sre-compliance-skill
description: "Use when auditing or implementing privacy-by-design and LGPD controls in Python systems, including telemetry minimization, PII handling, retention, backups, and access control."
---

# LGPD e Privacidade Operacional para Python

Esta skill orienta controles de engenharia de privacidade em código e
telemetria Python; não substitui análise jurídica. Considere dados do usuário,
logs de pipeline, diffs, prompts e saídas de modelos como potencialmente
sensíveis.

## Workflow

1. Localize dados pessoais, segredos, tokens, payloads brutos e identificadores
   em entradas, prompts, logs, traces, métricas, backups e dados de teste.
2. Minimize na origem: não envie nem registre dados que não sejam necessários
   para a tarefa.
3. Avalie retenção, acesso, ambiente, finalidade e possibilidade de vincular
   identificadores técnicos a pessoas.
4. Use sanitização antes do logger somente quando a coleta for necessária;
   redaction é proteção adicional, não justificativa para coletar tudo.
5. Teste que logs e erros não exponham conteúdo rejeitado, credenciais ou PII.
6. Documente riscos residuais e exija revisão apropriada antes de ligar dados
   reais ou ambientes operacionais.

## Regras para a aplicação

- Não registre prompts/respostas completos, corpos de request, logs CI brutos,
  diffs ou valores de campos de erro por padrão.
- Não use PII ou IDs de alta cardinalidade em labels de métricas.
- Credenciais ficam fora do código e de arquivos versionados; arquivos locais
  de ambiente não devem ser adicionados ao controle de versão.
- Defina retenção, controle de acesso, exclusão e trilha de auditoria antes de
  operar dados reais. O R1 local não oferece auditoria imutável nem controles
  operacionais.
- Não prometa conformidade LGPD somente com regex ou testes unitários.

## Referência de mascaramento

Consulte [lgpd-sre-compliance-skill.md](references/lgpd-sre-compliance-skill.md)
para o padrão Python do repositório. Minimize antes de mascarar e não duplique
implementações de sanitização sem necessidade.
