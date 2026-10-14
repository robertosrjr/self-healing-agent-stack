import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import agente
import config


class TestOpenRouterClient(unittest.TestCase):
    @patch("agente.registrar_execucao")
    @patch("agente.config.MAX_PASSOS", 3)
    @patch("agente.config.LLM_PROVIDER", "openrouter")
    def test_tool_call_uses_chat_completions_protocol(self, _registrar_execucao):
        chamada = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(
                name="somar",
                arguments=json.dumps({"a": 2, "b": 3}),
            ),
        )
        mensagem_assistente = SimpleNamespace(
            content=None,
            tool_calls=[chamada],
            refusal=None,
            model_dump=lambda **_: {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "call-1",
                        "type": "function",
                        "function": {
                            "name": "somar",
                            "arguments": '{"a": 2, "b": 3}',
                        },
                    }
                ],
            },
        )
        mensagem_final = SimpleNamespace(
            content="Resultado: 5",
            tool_calls=None,
            refusal=None,
            model_dump=lambda **_: {"role": "assistant", "content": "Resultado: 5"},
        )

        def resposta(mensagem, finish_reason):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=mensagem, finish_reason=finish_reason)],
                usage=SimpleNamespace(prompt_tokens=12, completion_tokens=5),
            )

        completar = unittest.mock.Mock(
            side_effect=[
                resposta(mensagem_assistente, "tool_calls"),
                resposta(mensagem_final, "stop"),
            ]
        )
        cliente = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=completar),
            )
        )
        ferramenta = agente.Ferramenta(
            nome="somar",
            descricao="Soma dois números",
            parametros={
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                },
                "required": ["a", "b"],
            },
            funcao=lambda a, b: str(a + b),
        )

        with patch.object(agente, "client", cliente), patch.object(
            config, "MODELO", "nvidia/nemotron-3-ultra-550b-a55b"
        ):
            result = agente.Agente(
                nome="teste",
                system="Você é um teste",
                ferramentas=[ferramenta],
            ).executar("Some 2 e 3")

        self.assertEqual(result, "Resultado: 5")
        payload = completar.call_args_list[0].kwargs
        self.assertEqual(payload["model"], "nvidia/nemotron-3-ultra-550b-a55b")
        self.assertEqual(payload["max_tokens"], config.OPENROUTER_MAX_TOKENS)
        self.assertEqual(payload["messages"][0], {"role": "system", "content": "Você é um teste"})
        self.assertEqual(payload["tools"][0]["type"], "function")
        second_messages = completar.call_args_list[1].kwargs["messages"]
        self.assertEqual(second_messages[-3]["role"], "assistant")
        self.assertEqual(second_messages[-2]["role"], "tool")
        self.assertEqual(second_messages[-2]["tool_call_id"], "call-1")
        self.assertEqual(second_messages[-2]["content"], "5")

    @patch("agente.registrar_execucao")
    @patch("agente.config.TOKEN_BUDGET", 20)
    @patch("agente.config.LLM_PROVIDER", "openrouter")
    def test_token_budget_stops_before_running_requested_tool(self, registrar_execucao):
        executar_ferramenta = unittest.mock.Mock(return_value="executada")
        ferramenta = agente.Ferramenta(
            nome="executar",
            descricao="Executa uma ação",
            parametros={"type": "object", "properties": {}},
            funcao=executar_ferramenta,
        )
        resposta = SimpleNamespace(
            stop_reason="tool_use",
            content=[
                SimpleNamespace(
                    type="tool_use",
                    id="call-1",
                    name="executar",
                    input={},
                )
            ],
            usage=SimpleNamespace(input_tokens=12, output_tokens=8),
            openrouter_message={"role": "assistant", "tool_calls": []},
        )
        agente_instance = agente.Agente(
            nome="teste",
            system="Você é um teste",
            ferramentas=[ferramenta],
        )

        with patch.object(agente_instance, "_chamar_modelo", return_value=resposta) as chamar:
            with self.assertRaisesRegex(RuntimeError, "Orçamento de tokens atingido"):
                agente_instance.executar("Faça a ação")

        chamar.assert_called_once()
        executar_ferramenta.assert_not_called()
        self.assertEqual(agente_instance.ultima_execucao["tokens_total"], 20)
        self.assertEqual(agente_instance.ultima_execucao["token_budget"], 20)
        self.assertIn("Orçamento de tokens atingido", registrar_execucao.call_args.args[3]["erro"])

    @patch("agente.registrar_execucao")
    @patch("agente.config.LLM_PROVIDER", "openrouter")
    def test_falha_do_modelo_e_registrada_e_propaga(self, registrar_execucao):
        agente_instance = agente.Agente(nome="teste", system="Você é um teste")

        with patch.object(
            agente_instance,
            "_chamar_modelo",
            side_effect=ConnectionError("indisponível"),
        ):
            with self.assertRaisesRegex(ConnectionError, "indisponível"):
                agente_instance.executar("Faça uma tarefa")

        self.assertEqual(agente_instance.ultima_execucao["erro"], "ConnectionError: indisponível")
        self.assertEqual(registrar_execucao.call_args.args[2], "[falha ao chamar o modelo]")

    def test_falha_de_ferramenta_retorna_erro_estruturado(self):
        ferramenta = agente.Ferramenta(
            nome="falhar",
            descricao="Sempre falha",
            parametros={"type": "object", "properties": {}},
            funcao=lambda: (_ for _ in ()).throw(ValueError("entrada inválida")),
        )
        agente_instance = agente.Agente(
            nome="teste",
            system="Você é um teste",
            ferramentas=[ferramenta],
        )
        bloco = SimpleNamespace(id="call-1", name="falhar", input={})

        resultado = agente_instance._executar_ferramenta({"falhar": ferramenta}, bloco)

        self.assertTrue(resultado["is_error"])
        self.assertIn("ValueError: entrada inválida", resultado["content"])

    def test_ferramenta_deve_retornar_texto(self):
        ferramenta = agente.Ferramenta(
            nome="retornar_numero",
            descricao="Retorna um número",
            parametros={"type": "object", "properties": {}},
            funcao=lambda: 42,
        )
        agente_instance = agente.Agente(
            nome="teste",
            system="Você é um teste",
            ferramentas=[ferramenta],
        )
        bloco = SimpleNamespace(
            id="call-1",
            name="retornar_numero",
            input={},
        )

        resultado = agente_instance._executar_ferramenta(
            {"retornar_numero": ferramenta},
            bloco,
        )

        self.assertTrue(resultado["is_error"])
        self.assertIn("deve retornar str", resultado["content"])


if __name__ == "__main__":
    unittest.main()
