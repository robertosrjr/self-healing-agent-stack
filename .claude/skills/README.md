# Skills de desenvolvimento

Este diretório reúne instruções reutilizáveis para orientar agentes de
desenvolvimento, revisão e documentação neste repositório. As skills são guias
de trabalho; **não são código executado pela aplicação** e não significam que
os controles descritos já estejam implementados na PoC.

## Como usar este catálogo

Escolha a skill de acordo com a tarefa e consulte o respectivo `SKILL.md` antes
de trabalhar. Algumas skills têm documentos complementares em `references/`.
As descrições abaixo indicam o escopo de cada uma; requisitos e procedimentos
completos permanecem nos arquivos vinculados.

## Skills adaptadas para Python

Estas skills foram ajustadas para o contexto Python do projeto, incluindo
orientações de arquitetura, código, testes e operação:

| Skill | Quando usar |
|---|---|
| [architecture-guidance](architecture-guidance/SKILL.md) | Delimitar módulos Python, direção de dependências, ports/adapters e uso parcimonioso de DDD. |
| [api-design-guidance](api-design-guidance/SKILL.md) | Desenhar APIs HTTP Python, contratos, erros, OpenAPI e compatibilidade. A API web ainda é futura na PoC. |
| [code-quality-guidance](code-quality-guidance/SKILL.md) | Revisar SOLID, legibilidade, tipagem, testabilidade e tratamento de erros em Python. |
| [testing-strategy-guidance](testing-strategy-guidance/SKILL.md) | Aplicar TDD, pytest e testes unitários ou de integração de desenvolvimento. |
| [quality-assurance-skills](quality-assurance-skills/SKILL.md) | Planejar estratégia de QA, camadas de automação, testes de contrato e gates de CI/CD. |
| [platform-practices-guidance](platform-practices-guidance/SKILL.md) | Preparar aplicações Python para plataforma, princípios Twelve-Factor e decisões síncrono/assíncrono. |
| [security-code-review](security-code-review/SKILL.md) | Revisar código Python para segredos, injeções, parsing inseguro, criptografia, dependências e erros sensíveis. |
| [resilience-checker-skill](resilience-checker-skill/SKILL.md) | Avaliar timeouts, retries, idempotência, concorrência e falhas explícitas em aplicações Python. |
| [sre-observability-skill](sre-observability-skill/SKILL.md) | Revisar logs, métricas, tracing, SLOs e privacidade de telemetria em Python. |
| [lgpd-sre-compliance-skill](lgpd-sre-compliance-skill/SKILL.md) | Aplicar privacidade por padrão, minimização de telemetria, tratamento de PII, retenção e controles LGPD em Python. |

## Skills de IA, privacidade e observabilidade agnósticas

Estas orientações tratam controles ou padrões que não dependem de uma
linguagem específica:

| Skill | Quando usar |
|---|---|
| [saif-skill](saif-skill/SKILL.md) | Avaliar segurança de sistemas com LLMs, injeção de prompt, governança de ferramentas, aprovação humana e sanitização de saídas. |
| [global-ai-principles](global-ai-principles/SKILL.md) | Avaliar direitos humanos, discriminação, privacidade e sustentabilidade em sistemas de IA. |
| [agnostic-logging](agnostic-logging/SKILL.md) | Definir logs estruturados, campos comuns, mascaramento de PII e orçamento de logs. |
| [agnostic-metrics](agnostic-metrics/SKILL.md) | Definir métricas, sinais SRE, cardinalidade, SLIs e SLOs sem dependência de linguagem. |
| [agnostic-tracing](agnostic-tracing/SKILL.md) | Projetar propagação W3C Trace Context, spans e convenções de tracing distribuído. |
| [agnostic-privacy](agnostic-privacy/SKILL.md) | Avaliar práticas operacionais de privacidade e sanitização de PII em telemetria. |

## Skills especializadas e condicionais

Use estas skills quando a atividade corresponder ao seu domínio; sua presença
não significa que a infraestrutura ou processo já exista neste repositório:

| Skill | Quando usar |
|---|---|
| [tech-documentation-skill](tech-documentation-skill/SKILL.md) | Criar ou revisar ADRs, DDAs, READMEs e manuais técnicos. |
| [docker-compose-spec-skill](docker-compose-spec-skill/SKILL.md) | Criar ou revisar ambientes multi-contêiner quando o projeto adotar Docker Compose. |
| [chaos-engineering](chaos-engineering/SKILL.md) | Planejar experimentos de resiliência com estado estável, hipótese, blast radius e condições de interrupção. Requer ambiente apropriado e seguro. |
| [service-modeling-skill](service-modeling-skill/SKILL.md) | Modelar Business Services e Service Offers usando a perspectiva de arquitetura de negócio TAGF/TOGAF. |

## Aplicabilidade ao projeto

- **Uso imediato:** skills Python de arquitetura, qualidade, testes, segurança,
  resiliência, privacidade e documentação podem orientar mudanças no protótipo.
- **Uso condicionado:** API, plataforma, Docker Compose, chaos engineering e
  modelagem de serviços tornam-se mais diretamente aplicáveis quando os
  respectivos componentes ou exercícios forem iniciados.
- **Orientação, não evidência:** seguir uma skill não substitui implementação,
  revisão de código, testes nem comprovação de controles. Webhooks, autorização
  externa, guardrails, deploy e promoção para Produção continuam sendo
  capacidades futuras descritas na SDD v5.

## Limites e manutenção

O catálogo resume o propósito das skills; cada `SKILL.md` é a fonte de
instruções detalhadas e deve ser consultado para a tarefa concreta. Ao alterar
uma skill, mantenha sua descrição alinhada à stack Python e atualize este
catálogo se o escopo ou a aplicabilidade mudar. Skills agnósticas devem
continuar identificadas como padrões de orientação, não como implementação
operacional.
