from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import config
import roteamento_jev


class TestRoteamentoJev(unittest.TestCase):
    @patch("roteamento_jev.config.TYPESAFE_API_KEY", "test-key")
    @patch("roteamento_jev.TypeSafeClient")
    def test_decidir_rota_retorna_choice_confidence_e_probabilities(self, mock_client_type):
        sdk_client = MagicMock()
        sdk_client.system_one.return_value = SimpleNamespace(
            choices={
                "rota": SimpleNamespace(
                    choice="analisar",
                    confidence=0.91,
                    probabilities={"analisar": 0.91, "explicar": 0.09},
                )
            }
        )
        mock_client_type.return_value.__enter__.return_value = sdk_client

        with patch.object(config, "TYPESAFE_MODEL", "jev-latest"):
            resultado = roteamento_jev.decidir_rota(
                "Quanto custam 3 itens de R$ 12?",
                {"fatos": ["preço unitário: R$ 12"]},
            )

        self.assertEqual(resultado["rota"], "analisar")
        self.assertEqual(resultado["confidence"], 0.91)
        self.assertEqual(resultado["probabilities"]["explicar"], 0.09)
        self.assertEqual(mock_client_type.call_args.kwargs, {"model": "jev-latest"})
        request = sdk_client.system_one.call_args.kwargs
        self.assertEqual(request["state"]["pergunta"], "Quanto custam 3 itens de R$ 12?")
        self.assertIn("rota", request["questions"])


if __name__ == "__main__":
    unittest.main()
