---
name: security-code-review
description: "Use when reviewing Python application changes for secrets, injection, unsafe deserialization, cryptography/TLS mistakes, dependency risks, or sensitive error leakage. For prompt injection and agent/tool governance use saif-skill."
---

# Revisão de Segurança de Código Python

Revise alterações Python com base em riscos presentes no código e nas
dependências reais. Esta skill cobre segurança de aplicação; segurança de
agentes e conteúdo não confiável também exige a skill SAIF.

## Áreas de revisão

### Segredos e configuração

- Procure chaves, tokens, senhas e credenciais em código, exemplos, testes,
  logs e arquivos de configuração versionados.
- Use variáveis de ambiente ou secret manager apropriado ao ambiente.
- Arquivos `.env` locais não devem ser commitados; verifique `.gitignore` e
  forneça somente placeholders em `.env.example`.

### Injeção e execução de comandos

- SQL: use parâmetros da biblioteca, nunca concatene entrada em consultas.
- Shell: evite `shell=True` com dados externos; prefira argumentos explícitos,
  allowlists e validação.
- Template, path e URL: valide nomes, escopo e destino; evite traversal, SSRF e
  interpolação de conteúdo não confiável.
- Não trate prompt injection como SQL injection; delimitação de contexto não
  substitui controles SAIF.

### Desserialização e parsing

- Não use `pickle` para conteúdo não confiável.
- Em YAML, use loader seguro; valide dados com schema explícito.
- Não confie em `eval`/`exec` ou em coerção permissiva de tipos.
- Valide JSON de modelos antes de usar em decisões; campos inesperados e enums
  inválidos devem falhar fechado.

### Criptografia, TLS e dependências

- Use primitives mantidas e protocolos seguros da biblioteca padrão/SDK; não
  escreva criptografia própria nem desative validação TLS.
- Revise versões, origem e necessidade de dependências adicionadas.
- Não atribua vulnerabilidade sem evidência do uso e do caminho de ataque.

### Erros e logs

- Respostas externas não devem incluir traceback, segredo, prompt ou payload
  rejeitado. Exponha mensagens técnicas apenas onde a política permitir.
- Preserve erros operacionais de forma explícita; não os transforme em
  resultado aprovado ou fallback de sucesso.
- Verifique que testes não imprimem nem registram credenciais reais.

## Como reportar

Indique localização, pré-condições, impacto, confiança e remediação mínima.
Diferencie vulnerabilidade explorável de endurecimento preventivo. Não descreva
capacidades de autorização, guardrails ou auditoria que ainda não existem.
