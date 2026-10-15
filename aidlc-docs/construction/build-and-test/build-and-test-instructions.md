# Instruções de Build e Teste — U1 Maker-Checker

## Pré-requisitos

- Python instalado e disponível no terminal.
- A pasta `application/` do repositório.
- Para testes, dependências de desenvolvimento instaladas pelo manifesto
  `application/requirements-dev.txt`.
- Não são necessárias chaves reais de provedores: os testes automatizados não
  devem fazer chamadas de rede a LLMs.

## Build

O projeto não possui etapa de compilação ou empacotamento separada. A partir da
raiz do repositório, instale as dependências e verifique a compilação sintática:

```powershell
Set-Location application
python -m pip install -r requirements-dev.txt
python -m compileall -q .
```

Sucesso: os comandos terminam com código zero. `compileall` não cria artefato
de distribuição; pode gerar arquivos `__pycache__` locais.

## Testes unitários

Execute a suíte inteira a partir de `application/`:

```powershell
python -m pytest tests -q
```

Resultado observado nesta execução: 29 testes aprovados. A saída do pytest
mostra contagens de testes aprovados e falhos; ao ocorrer falha, examine o caso
e a mensagem, corrija a causa e repita o comando.

Para executar apenas o fluxo Maker-Checker:

```powershell
python -m pytest tests/test_maker_checker.py -q
```

Os testes cobrem contratos estritos, JSON e schema inválidos, transições
aprovadas/rejeitadas/inconclusivas, propagação de falha do worker, não
invocação do Checker após erro do Maker e ausência de valores rejeitados nas
mensagens de validação.

## Integração

R1 não possui serviços, banco, fila, API HTTP ou integração real com provedor
externo a inicializar. O encadeamento Maker-Checker é testado com workers
injetáveis; por isso, testes de integração externos são **não aplicáveis** a
este incremento. Não há comandos de inicialização ou limpeza de infraestrutura.

## Outros níveis de teste

- Performance e carga: não aplicáveis; não há requisito de desempenho de
  produção definido para R1.
- Contrato HTTP: não aplicável; R1 expõe uma função local e contratos Pydantic,
  sem API ou microserviços.
- End-to-end: não aplicável; o fluxo não está ligado a uma jornada de CI/CD.
- Verificações de segurança delimitadas: ver
  [security-test-instructions.md](./security-test-instructions.md).
