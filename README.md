# Orquestrador de agentes — estudo e arquitetura-alvo

[![Stars](https://img.shields.io/github/stars/robertosrjr/self-healing-agent-stack?style=social)](https://github.com/robertosrjr/self-healing-agent-stack/stargazers)
[![Forks](https://img.shields.io/github/forks/robertosrjr/self-healing-agent-stack?style=social)](https://github.com/robertosrjr/self-healing-agent-stack/network/members)
[![Issues abertas](https://img.shields.io/github/issues/robertosrjr/self-healing-agent-stack)](https://github.com/robertosrjr/self-healing-agent-stack/issues)
[![Último commit](https://img.shields.io/github/last-commit/robertosrjr/self-healing-agent-stack)](https://github.com/robertosrjr/self-healing-agent-stack/commits/main)
[![Linguagem principal](https://img.shields.io/github/languages/top/robertosrjr/self-healing-agent-stack)](https://github.com/robertosrjr/self-healing-agent-stack)
![Status do projeto](https://img.shields.io/badge/status-prot%C3%B3tipo%20de%20estudo-blue)
[![Arquitetura-alvo](https://img.shields.io/badge/arquitetura-alvo%20Self--Healing%20(SDD%20v2)-lightgrey)](docs/sdd/sdd_orquestrador_agentes_v2.md)
[![Metodologia IA-DLC](https://img.shields.io/badge/metodologia-IA--DLC-0A7B83)](aidlc-docs/aidlc-state.md)
[![SDD v2](https://img.shields.io/badge/arquitetura-SDD%20v2-6f42c1)](docs/sdd/sdd_orquestrador_agentes_v2.md)
![Runtime](https://img.shields.io/badge/runtime-ReAct-6f42c1)
![Provedores LLM](https://img.shields.io/badge/LLM-Anthropic%20%7C%20OpenRouter-412991)

Este repositório é um projeto de estudo sobre **orquestração de agentes de IA
em ambientes corporativos**, com foco em revisão de código e auto-remediação
de falhas de CI/CD. A arquitetura-alvo está descrita no
[SDD v2](docs/sdd/sdd_orquestrador_agentes_v2.md) e nas
[diretrizes do estudo](docs/sdd/diretrizes_estudo_orquestracao_agentes.md).
Ela combina agentes especialistas com controles determinísticos para apoiar
diagnóstico, proposta de correções, testes e promoção governada de mudanças.

O código em `application/` é atualmente um **protótipo didático do runtime e
do padrão orquestrador-trabalhadores**. Ele não implementa ainda a esteira de
auto-remediação nem deve ser considerado pronto para uso corporativo ou
produção.

## Contexto do projeto

Modelos de linguagem podem analisar informações e propor ações, mas seus
resultados são probabilísticos. Em fluxos corporativos — especialmente quando
envolvem código, infraestrutura e produção — isso cria uma **lacuna de
confiança**: a organização precisa saber quais ações podem ocorrer, com que
evidências, sob quais permissões e com qual possibilidade de revisão.

O projeto estuda como fechar essa lacuna por meio de um sistema multiagente
que separa o raciocínio do modelo das decisões de controle. Os agentes
produzem análises e achados estruturados; autorização, validação de qualidade,
alterações efetivas e promoção de ambientes ficam a cargo de controles
determinísticos e, quando necessário, de aprovação humana.

### Problema que a arquitetura-alvo pretende resolver

Uma falha de pipeline ou uma alteração em um Pull Request pode exigir análise
de logs, investigação do contexto do repositório, revisão de arquitetura,
qualidade, segurança e conformidade, além de testes e decisões de liberação.
O objetivo é coordenar essas atividades em um fluxo rastreável, em vez de
confiar uma ação operacional diretamente à resposta livre de um único modelo.

Para falhas de CI/CD, o fluxo-alvo recebe o evento e os logs, investiga a causa
provável, propõe uma correção focada, valida-a com testes de regressão e só
avança quando os gates definidos forem satisfeitos. Para revisão de código,
agentes especialistas podem produzir achados de arquitetura, qualidade,
segurança e LGPD; um quality gate determinístico consolida esses achados, sem
delegar aos agentes a aprovação ou o merge do Pull Request.

### Valor esperado

A arquitetura proposta pretende:

- organizar diagnóstico, proposta de correção e validação em etapas
  verificáveis;
- tornar explícitas as evidências, os resultados de testes e as decisões do
  fluxo;
- limitar ações por políticas de menor privilégio e *deny-by-default*;
- impedir que um LLM autorize a si próprio, altere código ou promova uma
  versão sem os controles exigidos;
- permitir revisão humana e aprovação obrigatória para promoção a Produção,
  conforme as regras do ambiente.

Esse é o valor pretendido para o sistema-alvo, não uma garantia de redução de
incidentes ou de tempo de resolução já medida pelo protótipo.

### Público e cenário de uso

O estudo é relevante para equipes de DevOps e plataforma, desenvolvimento,
QA/liberação, segurança, governança e auditoria. O cenário de referência é a
integração do fluxo com CI/CD: eventos de falha iniciam o diagnóstico e
Pull Requests podem ser avaliados por especialistas, com achados estruturados
e decisões finais submetidas a regras explícitas.

## Arquitetura-alvo

```text
Falha no CI/CD
      │
      ▼
Webhook / gatilho de evento
      │
      ▼
Orquestrador de auto-remediação
      ├── Diagnóstico da falha e causa raiz
      ├── Proposta de patch
      ├── Testes de regressão
      └── PR / implantação em DEV e STAGING
                     │
                     ▼
          Quality gate determinístico
                     │
                     ▼
          Aprovação humana para PROD
```

O LLM propõe análises e resultados estruturados; controles determinísticos
externos devem autorizar ações, validar testes e decidir os gates. Agentes não
devem aprovar ou implantar mudanças em Produção por conta própria.

## Estado atual

O protótipo demonstra:

- um loop ReAct que alterna entre chamadas ao modelo e ferramentas Python;
- agentes especialistas e delegação pelo orquestrador;
- provedores Anthropic e OpenRouter, além de roteamento com Jev/TypeSafe;
- ferramentas locais de exemplo para busca, cálculo e contagem de palavras;
- limite de iterações (`MAX_PASSOS`, padrão `10`);
- orçamento de tokens por execução de agente (`TOKEN_BUDGET`, padrão `20000`);
- registro de métricas e histórico das execuções.

Ainda não estão implementados os componentes centrais do SDD v2: webhook de
falha de CI/CD, Diagnostic Worker integrado ao repositório e aos logs,
geração/aplicação de patches, execução isolada de testes, PEP/PDP com
políticas *deny-by-default*, guardrails, trilha de auditoria imutável,
integração de PR/deploy ou aprovação de Produção.

### Diferenças em relação aos parâmetros do SDD

O SDD v2 especifica limites e controles para o sistema-alvo, incluindo
`MAX_PASSOS` de 5 por subagente, até 2 tentativas de remediação e orçamento de
25.000 tokens por evento. O protótipo, por outro lado, usa `MAX_PASSOS=10` e
`TOKEN_BUDGET=20000` **por execução de agente**. Esses valores não equivalem a
um limite agregado por evento; precisam ser revistos quando o fluxo de
auto-remediação for implementado.

O orçamento de tokens é verificado com base no uso reportado pelo provedor
após cada resposta. Assim, ele interrompe ferramentas e iterações seguintes
quando aplicável, mas não cancela uma chamada ao modelo já em andamento.

## Documentos do estudo

- [Roadmap do produto — marcos, critérios e indicadores](docs/roadmap_produto.md)
- [SDD v2 — arquitetura-alvo e fases de implementação](docs/sdd/sdd_orquestrador_agentes_v2.md)
- [Diretrizes do estudo de orquestração](docs/sdd/diretrizes_estudo_orquestracao_agentes.md)
- [Plano do Passo 1 — runtime ReAct](docs/plano_passo_1_runtime.md)

## Código da aplicação

| Arquivo | Responsabilidade |
|---|---|
| [application/agente.py](application/agente.py) | Loop ReAct, chamadas ao modelo, execução de ferramentas e controles do runtime. |
| [application/ferramentas.py](application/ferramentas.py) | Ferramentas locais usadas no protótipo. |
| [application/especialistas.py](application/especialistas.py) | Agentes especialistas de pesquisa, análise, redação e revisão. |
| [application/orquestrador.py](application/orquestrador.py) | Coordenação do fluxo de demonstração e delegação a especialistas. |
| [application/roteamento_jev.py](application/roteamento_jev.py) | Roteamento entre análise quantitativa e explicação. |
| [application/config.py](application/config.py) | Configuração de provedores, modelos e limites de execução. |
| [application/main.py](application/main.py) | Entrada para executar a demonstração interativa. |

## Executar o protótipo

No PowerShell, a partir da raiz do repositório:

```powershell
Set-Location application
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite `application/.env` e configure a chave do provedor de LLM escolhido. O
provedor padrão é Anthropic, a menos que `LLM_PROVIDER` ou uma chave do
OpenRouter determinem o contrário. O roteamento Jev fica ativo por padrão e
requer `TYPESAFE_API_KEY`; para desativá-lo, defina:

```env
USAR_JEV_ROTEAMENTO=false
```

Inicie a pergunta de demonstração ou informe a sua:

```powershell
python main.py
python main.py "Quanto eu gastaria por mês carregando um carro elétrico em casa?"
```

As ferramentas pesquisam somente uma pequena base local de demonstração. Os
dados não são uma fonte atualizada nem substituem pesquisa ou validação de
informações reais.

## Executar os testes

Na pasta `application`:

```powershell
python -m pytest tests -q
```

Os testes exercitam o loop e os fluxos com dependências externas simuladas;
eles não validam uma integração real com CI/CD ou implantação.

## Roteiro previsto no SDD v2

1. **Core ReAct e diagnóstico:** exercitar o runtime e implementar o diagnóstico
   de uma falha de pipeline a partir de evento, logs e contexto do código.
2. **Correção e QA:** propor um patch limitado à causa raiz e executar testes
   de regressão em ambiente isolado.
3. **Eventos e Staging:** integrar o gatilho de CI/CD, criar PR e automatizar a
   implantação em Homologação após os gates definidos.
4. **Governança e Produção:** adicionar autorização externa, guardrails,
   auditoria e aprovação humana obrigatória para promoção de Produção.
