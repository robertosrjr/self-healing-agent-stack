import os
import unittest
from unittest.mock import patch

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from orquestrador import executar_fluxo_padrao_json, validar_resposta_final


class TestOrquestradorFlow(unittest.TestCase):
    def test_validar_resposta_final_ok(self):
        resultado = validar_resposta_final("Quanto custa energia solar?", "Resposta curta e clara.", 150)
        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["motivo"], "ok")

    def test_validar_resposta_final_excede_limite(self):
        texto = "palavra " * 151
        resultado = validar_resposta_final("Pergunta?", texto, 150)
        self.assertFalse(resultado["ok"])
        self.assertIn("limite", str(resultado))

    @patch("orquestrador.config.TYPESAFE_API_KEY", "test-typesafe-key")
    @patch(
        "orquestrador.decidir_rota",
        return_value={"rota": "analisar", "confidence": 0.97, "probabilities": {}},
    )
    @patch("orquestrador.delegar")
    def test_executar_fluxo_padrao_json(self, mock_delegar, _mock_rota):
        mock_delegar.side_effect = [
            '{"fatos": ["energia solar"], "faltantes": []}',
            '{"pergunta": "Quanto custa?", "fatos_usados": ["energia solar"], "calculos": ["550 * 5"], "resultado": "R$ 2.750"}',
            "Resposta clara e objetiva em até 150 palavras.",
            "Resposta clara e objetiva em até 150 palavras.",
        ]

        resultado = executar_fluxo_padrao_json("Quanto custa energia solar?")

        self.assertIn("pergunta", resultado)
        self.assertIn("resposta", resultado)
        self.assertTrue(resultado["valido"])
        self.assertEqual(resultado["palavras"], 8)

    @patch("orquestrador.config.TYPESAFE_API_KEY", "")
    @patch("orquestrador.delegar")
    def test_fluxo_rejeita_roteamento_jev_sem_chave(self, mock_delegar):
        with self.assertRaisesRegex(RuntimeError, "TYPESAFE_API_KEY"):
            executar_fluxo_padrao_json("Pergunta?")
        mock_delegar.assert_not_called()

    @patch("orquestrador.config.TYPESAFE_API_KEY", "test-typesafe-key")
    @patch(
        "orquestrador.decidir_rota",
        return_value={"rota": "explicar", "confidence": 0.96, "probabilities": {}},
    )
    @patch("orquestrador.delegar")
    def test_fluxo_explica_sem_chamar_analista(self, mock_delegar, _mock_rota):
        mock_delegar.side_effect = [
            '{"fatos": ["IA generativa produz conteúdo"], "faltantes": []}',
            "IA generativa cria conteúdo novo a partir de padrões aprendidos.",
            "IA generativa cria conteúdo novo a partir de padrões aprendidos.",
        ]

        resultado = executar_fluxo_padrao_json("O que é IA generativa?")

        self.assertTrue(resultado["valido"])
        self.assertEqual(
            [call.args[0] for call in mock_delegar.call_args_list],
            ["pesquisador", "redator", "revisor"],
        )


if __name__ == "__main__":
    unittest.main()
