import json
import threading
import time
import unittest

from padroes_multiagente import (
    HandoffService,
    MagenticService,
    MultiAgentContractError,
    executar_paralelo,
)


def _json(value):
    return json.dumps(value)


class TestExecucaoParalela(unittest.TestCase):
    def test_executa_workers_com_concorrencia_limitada_e_ordem_estavel(self):
        lock = threading.Lock()
        active = 0
        max_active = 0

        def worker(nome):
            def executar(tarefa):
                nonlocal active, max_active
                with lock:
                    active += 1
                    max_active = max(max_active, active)
                time.sleep(0.01)
                with lock:
                    active -= 1
                return f"{nome}: {tarefa}"

            return executar

        workers = {f"agent-{index}": worker(f"agent-{index}") for index in range(5)}

        result = executar_paralelo("analisar", workers, max_concorrencia=2)

        self.assertEqual(max_active, 2)
        self.assertEqual([item["agent"] for item in result], list(workers))
        self.assertEqual(result[0]["result"], "agent-0: analisar")

    def test_rejeita_entrada_vazia_e_limite_invalido(self):
        with self.assertRaises(ValueError):
            executar_paralelo("tarefa", {}, max_concorrencia=2)
        with self.assertRaises(ValueError):
            executar_paralelo("tarefa", {"agent": lambda _: "ok"}, max_concorrencia=0)
        with self.assertRaises(ValueError):
            executar_paralelo(" ", {"agent": lambda _: "ok"}, max_concorrencia=1)

    def test_propaga_falha_de_worker_sem_resultado_de_sucesso(self):
        failure = RuntimeError("worker indisponível")

        def worker(_):
            raise failure

        with self.assertRaisesRegex(RuntimeError, "worker indisponível"):
            executar_paralelo("tarefa", {"agent": worker}, max_concorrencia=1)


class TestHandoff(unittest.TestCase):
    def test_transfere_contexto_ate_resposta_final_validada(self):
        prompts = []

        def analyst(prompt):
            prompts.append(prompt)
            return _json({"next_agent": "reviewer", "response": "analysis ready"})

        def reviewer(prompt):
            prompts.append(prompt)
            return _json({"next_agent": None, "response": "resultado revisado"})

        result = HandoffService(
            {"analyst": analyst, "reviewer": reviewer},
            max_handoffs=1,
        ).executar("analise a tarefa", "analyst")

        self.assertEqual(result["result"], "resultado revisado")
        self.assertEqual([item["agent"] for item in result["handoffs"]], ["analyst", "reviewer"])
        self.assertIn("analysis ready", prompts[1])
        self.assertIn("<external_data>", prompts[0])

    def test_rejeita_destino_desconhecido_e_ciclo(self):
        unknown = HandoffService(
            {"analyst": lambda _: _json({"next_agent": "missing", "response": "x"})}
        )
        with self.assertRaisesRegex(MultiAgentContractError, "unknown_handoff_agent"):
            unknown.executar("tarefa", "analyst")

        cycle = HandoffService(
            {"analyst": lambda _: _json({"next_agent": "analyst", "response": "x"})}
        )
        with self.assertRaisesRegex(MultiAgentContractError, "handoff_cycle"):
            cycle.executar("tarefa", "analyst")

    def test_limita_transferencias_e_rejeita_json_invalido(self):
        calls = []
        service = HandoffService(
            {
                "first": lambda _: calls.append("first")
                or _json({"next_agent": "second", "response": "continue"}),
                "second": lambda _: _json({"next_agent": None, "response": "done"}),
            },
            max_handoffs=0,
        )
        with self.assertRaisesRegex(MultiAgentContractError, "handoff_limit"):
            service.executar("tarefa", "first")
        self.assertEqual(calls, ["first"])

        invalid = HandoffService({"agent": lambda _: '{"next_agent": "secret'})
        with self.assertRaises(MultiAgentContractError) as raised:
            invalid.executar("tarefa", "agent")
        self.assertEqual(raised.exception.code, "invalid_json")
        self.assertNotIn("secret", str(raised.exception))


class TestPlanejamentoMagentic(unittest.TestCase):
    def test_atualiza_ledger_adiciona_tarefas_e_respeita_dependencias(self):
        plans = iter(
            [
                {
                    "new_tasks": [
                        {"task_id": "a", "agent": "analyst", "description": "A", "depends_on": []},
                        {"task_id": "b", "agent": "reviewer", "description": "B", "depends_on": ["a"]},
                    ],
                    "task_order": ["a", "b"],
                    "done": False,
                },
                {
                    "new_tasks": [
                        {"task_id": "c", "agent": "reviewer", "description": "C", "depends_on": ["a"]}
                    ],
                    "task_order": ["b", "c"],
                    "done": False,
                },
                {"new_tasks": [], "task_order": ["c"], "done": False},
                {"new_tasks": [], "task_order": [], "done": True},
            ]
        )
        executed = []

        def worker(name):
            def run(prompt):
                executed.append(name)
                return f"result-{name}"

            return run

        service = MagenticService(
            planner=lambda _: _json(next(plans)),
            workers={"analyst": worker("analyst"), "reviewer": worker("reviewer")},
        )

        result = service.executar("complete the work")

        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(executed, ["analyst", "reviewer", "reviewer"])
        self.assertEqual([task["task_id"] for task in result["tasks"]], ["a", "b", "c"])
        self.assertTrue(all(task["status"] == "COMPLETED" for task in result["tasks"]))

    def test_rejeita_ciclo_de_dependencias_antes_de_executar_workers(self):
        calls = []
        plan = {
            "new_tasks": [
                {"task_id": "a", "agent": "worker", "description": "A", "depends_on": ["b"]},
                {"task_id": "b", "agent": "worker", "description": "B", "depends_on": ["a"]},
            ],
            "task_order": ["a", "b"],
            "done": False,
        }
        service = MagenticService(
            planner=lambda _: _json(plan),
            workers={"worker": lambda _: calls.append("worker")},
        )

        with self.assertRaisesRegex(MultiAgentContractError, "dependency_cycle"):
            service.executar("tarefa")
        self.assertEqual(calls, [])

    def test_rejeita_agente_desconhecido_e_ordem_incompleta(self):
        bad_agent_plan = {
            "new_tasks": [
                {"task_id": "a", "agent": "unknown", "description": "A", "depends_on": []}
            ],
            "task_order": ["a"],
            "done": False,
        }
        service = MagenticService(lambda _: _json(bad_agent_plan), {"worker": lambda _: "ok"})
        with self.assertRaisesRegex(MultiAgentContractError, "unknown_task_agent"):
            service.executar("tarefa")

        bad_order_plan = {
            "new_tasks": [
                {"task_id": "a", "agent": "worker", "description": "A", "depends_on": []}
            ],
            "task_order": [],
            "done": False,
        }
        service = MagenticService(lambda _: _json(bad_order_plan), {"worker": lambda _: "ok"})
        with self.assertRaisesRegex(MultiAgentContractError, "invalid_task_order"):
            service.executar("tarefa")

    def test_limita_iteracoes_sem_conclusao_do_planejador(self):
        plan = {
            "new_tasks": [
                {"task_id": "a", "agent": "worker", "description": "A", "depends_on": []}
            ],
            "task_order": ["a"],
            "done": False,
        }
        service = MagenticService(
            planner=lambda _: _json(plan),
            workers={"worker": lambda _: "ok"},
            max_iterations=1,
        )

        with self.assertRaisesRegex(MultiAgentContractError, "iteration_limit"):
            service.executar("tarefa")

    def test_worker_error_propagates(self):
        failure = RuntimeError("worker failed")
        plan = {
            "new_tasks": [
                {"task_id": "a", "agent": "worker", "description": "A", "depends_on": []}
            ],
            "task_order": ["a"],
            "done": False,
        }
        service = MagenticService(
            planner=lambda _: _json(plan),
            workers={"worker": lambda _: (_ for _ in ()).throw(failure)},
        )

        with self.assertRaisesRegex(RuntimeError, "worker failed"):
            service.executar("tarefa")


if __name__ == "__main__":
    unittest.main()
