import os
import unittest
from unittest.mock import patch

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from orquestrador import (
    _planejador_magentic,
    executar_fluxo_padrao_json,
    executar_handoff_especialistas,
    executar_magentic,
    executar_paralelo_especialistas,
    validar_resposta_final,
)


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

    @patch("orquestrador.config.MAX_TRABALHOS_PARARELOS", 1)
    @patch("orquestrador.delegar", side_effect=lambda nome, _: f"resultado-{nome}")
    def test_executar_especialistas_em_paralelo(self, _mock_delegar):
        result = executar_paralelo_especialistas(
            "tarefa independente",
            ["pesquisador", "redator"],
        )

        self.assertEqual(
            result,
            [
                {"agent": "pesquisador", "result": "resultado-pesquisador"},
                {"agent": "redator", "result": "resultado-redator"},
            ],
        )

    def test_paralelo_rejeita_especialista_desconhecido_ou_duplicado(self):
        with self.assertRaisesRegex(ValueError, "unknown_agent"):
            executar_paralelo_especialistas("tarefa", ["inexistente"])
        with self.assertRaisesRegex(ValueError, "duplicate_agent"):
            executar_paralelo_especialistas("tarefa", ["pesquisador", "pesquisador"])

    @patch(
        "orquestrador.delegar",
        side_effect=[
            '{"next_agent":"revisor","response":"analysis ready"}',
            '{"next_agent":null,"response":"reviewed result"}',
        ],
    )
    def test_executar_handoff_entre_especialistas(self, mock_delegar):
        result = executar_handoff_especialistas("tarefa", "pesquisador")

        self.assertEqual(result["result"], "reviewed result")
        self.assertEqual(
            [call.args[0] for call in mock_delegar.call_args_list],
            ["pesquisador", "revisor"],
        )

    @patch.object(
        _planejador_magentic,
        "executar",
        side_effect=[
            '{"new_tasks":[{"task_id":"t1","agent":"pesquisador",'
            '"description":"find facts","depends_on":[]}],'
            '"task_order":["t1"],"done":false}',
            '{"new_tasks":[],"task_order":[],"done":true}',
        ],
    )
    @patch(
        "orquestrador.delegar",
        return_value="facts found",
    )
    def test_executar_magentic_com_workers_configurados(self, mock_delegar, _mock_planner):
        result = executar_magentic("research task")

        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["tasks"][0]["result"], "facts found")
        mock_delegar.assert_called_once()


if __name__ == "__main__":
    unittest.main()
