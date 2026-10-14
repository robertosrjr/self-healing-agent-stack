# Regras de Negócio — U1 Maker-Checker

1. **Validar antes de usar:** nenhuma entrada é enviada ao primeiro trabalhador
   antes de passar pelo contrato de entrada.
2. **Validar cada fronteira:** cada resposta estruturada é parseada e validada
   antes de ser consumida por outra etapa ou retornada ao chamador.
3. **Falhar fechado:** JSON inválido, campos obrigatórios ausentes, tipos
   incompatíveis, enums desconhecidos e propriedades proibidas bloqueiam o
   fluxo.
4. **Sem Checker sobre dados inválidos:** o Checker não é chamado quando a
   saída do Maker falha validação.
5. **Decisão enumerada:** o Checker só pode retornar `APPROVED`, `REJECTED` ou
   `INCONCLUSIVE`; qualquer outro valor é erro de contrato.
6. **Aprovação explícita:** apenas `decision=APPROVED` gera `status=APPROVED`.
   Rejeição ou inconclusão não é exceção de sistema, mas nunca permite avanço.
7. **Sem aprovação por omissão:** campo ausente, null ou tipo incorreto não
   pode receber default que resulte em aprovação.
8. **Sem retry corretivo nesta unidade:** resposta inválida encerra a execução
   de forma explícita; retry de chamada ao modelo não é usado para mascarar
   falha de contrato.
9. **Sem autoridade do LLM:** Maker e Checker não autorizam ferramenta, não
   aplicam mudança e não controlam políticas.
10. **Contexto delimitado:** o Checker recebe apenas entrada validada e saída
    Maker validada necessária à revisão; não recebe cadeia privada de
    raciocínio do Maker.
11. **Compatibilidade:** mudanças no fluxo devem preservar os testes e
    comportamentos preexistentes do runtime.
12. **Escopo limitado:** nenhum evento CI/CD, patch de código, worktree, deploy,
    autorização externa ou guardrail é implementado em R1.
