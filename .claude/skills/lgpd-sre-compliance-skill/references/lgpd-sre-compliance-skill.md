# LGPD e privacidade em telemetria Python

Guia de engenharia; não é aconselhamento jurídico. Minimize os dados na origem
e defina finalidade, acesso e retenção antes de enviar dados a logs ou serviços
externos.

## 1. Princípios de implementação

- Não registre corpos de request/response, prompts, respostas, logs brutos de
  pipeline ou diffs por padrão.
- Trate tokens, chaves de API, senhas e cookies como dados que nunca devem ser
  registrados.
- Trate IDs técnicos como potencialmente pessoais se puderem ser associados a
  uma pessoa.
- Redaction é medida complementar: não deve substituir minimização.
- Defina retenção, exclusão, segregação de ambientes e acesso para telemetria
  operacional real.

## 2. Localize fluxos de dados

Revise campos, variáveis e chamadas a `logging`, exporters e clientes externos
para valores como CPF, email, telefone, endereço, IP, username, token, chave de
API, log CI, prompt e conteúdo de repositório. Inclua dados de testes e
exemplos; nunca use credenciais reais em testes.

## 3. Referência Python para mascaramento defensivo

Use somente como exemplo limitado, depois de decidir que o dado precisa ser
registrado. Substitua segredos e conteúdo irrelevante antes de chamar logger;
não dependa de regex para classificar todos os dados pessoais.

```python
import re

CPF_PATTERN = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
EMAIL_PATTERN = re.compile(
    r"\b([A-Za-z0-9])[A-Za-z0-9._%+-]*([A-Za-z0-9])"
    r"(@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b"
)
BEARER_PATTERN = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]+=*", re.IGNORECASE)


def sanitize_log_text(value: str) -> str:
    sanitized = BEARER_PATTERN.sub("Bearer [REDACTED]", value)
    sanitized = CPF_PATTERN.sub("[REDACTED_CPF]", sanitized)
    return EMAIL_PATTERN.sub(r"\1***\2\3", sanitized)
```

Teste separadamente formatos com e sem pontuação, strings vazias, limites
adjacentes e casos falsos positivos. Nunca registre cartão, CPF, tokens ou
senhas em exemplos reais só porque existe sanitizador.

## 4. Logging seguro

```python
logger.info(
    "maker_checker_completed",
    extra={"request_id": safe_request_id, "status": status},
)
```

O exemplo ilustra metadados; configure formatter e filtros apenas se houver
consumidor operacional. Evite `logger.info("prompt=%s", prompt)` e exceções que
possam serializar o payload recebido.

## 5. Verificação e limites

- Faça testes para garantir que valores sentinela não aparecem em logs/erros.
- Audite acesso, retenção e exportação antes de conectar logs centralizados.
- Regex não detecta todos os dados sensíveis, pode ter falsos positivos e não
  garante conformidade.
- O protótipo R1 não implementa retenção, controle de acesso operacional ou
  trilha de auditoria imutável.
