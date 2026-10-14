import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from agente import HISTORICO_PATH, registrar_execucao, resumo_historico


class TestHistoricoExecucao(unittest.TestCase):
    def setUp(self):
        self.original = HISTORICO_PATH
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name) / "historico_execucoes.json"
        import agente
        agente.HISTORICO_PATH = self.temp_path

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_registrar_execucao_e_resumo(self):
        registro = registrar_execucao("teste", "pergunta", "resposta", {"tempo_segundos": 1.5, "input_tokens": 10, "output_tokens": 20})
        self.assertIn("agente", registro)
        self.assertEqual(registro["agente"], "teste")

        resumo = resumo_historico()
        self.assertEqual(resumo["total_execucoes"], 1)
        self.assertEqual(resumo["input_tokens_total"], 10)
        self.assertEqual(resumo["output_tokens_total"], 20)


if __name__ == "__main__":
    unittest.main()
