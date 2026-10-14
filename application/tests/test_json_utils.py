import os
import unittest

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from agente import extrair_json


class TestExtrairJson(unittest.TestCase):
    def test_extrai_json_bruto(self):
        texto = '{"fatos": ["a", "b"], "faltantes": []}'
        self.assertEqual(extrair_json(texto), {"fatos": ["a", "b"], "faltantes": []})

    def test_extrai_json_em_markdown(self):
        texto = '```json\n{"pergunta": "x", "resultado": 42}\n```'
        self.assertEqual(extrair_json(texto), {"pergunta": "x", "resultado": 42})

    def test_extrai_json_com_texto_extra(self):
        texto = 'Resposta: {"calculos": ["2 + 2"], "resultado": 4}'
        self.assertEqual(extrair_json(texto), {"calculos": ["2 + 2"], "resultado": 4})

    def test_extrai_json_raises_on_invalid(self):
        with self.assertRaises(ValueError):
            extrair_json('isso não é json')


if __name__ == "__main__":
    unittest.main()
