import os
import unittest

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from contratos_maker_checker import (
    ContractValidationError,
    MakerCheckerRequest,
    MakerCheckerResponse,
    validate_contract,
)
from maker_checker import MakerCheckerService
from especialistas import ESPECIALISTAS


class TestMakerCheckerContracts(unittest.TestCase):
    def test_maker_and_checker_are_not_available_for_direct_orchestrator_delegation(self):
        self.assertNotIn("maker", ESPECIALISTAS)
        self.assertNotIn("checker", ESPECIALISTAS)

    def test_rejects_extra_request_fields_without_echoing_values(self):
        secret_value = "do-not-leak-this-value"
        with self.assertRaises(ContractValidationError) as raised:
            validate_contract(
                MakerCheckerRequest,
                {
                    "request_id": "req-1",
                    "task": "Review result",
                    "context": {},
                    "unexpected": secret_value,
                },
            )

        self.assertEqual(raised.exception.code, "schema_invalid")
        self.assertIn("unexpected", str(raised.exception))
        self.assertNotIn(secret_value, str(raised.exception))

    def test_rejects_non_json_context(self):
        with self.assertRaises(ContractValidationError) as raised:
            validate_contract(
                MakerCheckerRequest,
                {"request_id": "req-1", "task": "Review", "context": {"bad": (1, 2)}},
            )

        self.assertEqual(raised.exception.code, "schema_invalid")
        self.assertIn("context", raised.exception.paths)

    def test_rejects_non_string_nested_object_keys(self):
        with self.assertRaises(ContractValidationError):
            validate_contract(
                MakerCheckerRequest,
                {"request_id": "req-1", "task": "Review", "context": {"nested": {1: "value"}}},
            )

    def test_response_requires_checker_for_non_inconclusive_maker(self):
        with self.assertRaises(ValueError):
            MakerCheckerResponse(
                request_id="req-1",
                status="APPROVED",
                maker_result={"status": "COMPLETED", "payload": {}, "evidence": []},
                checker_result=None,
            )


class TestMakerCheckerService(unittest.TestCase):
    def setUp(self):
        self.request = {
            "request_id": "req-1",
            "task": "Summarize the provided facts",
            "context": {"facts": ["fact-1"]},
        }

    def test_valid_flow_passes_validated_maker_output_to_checker(self):
        calls = []

        def maker(prompt):
            calls.append(("maker", prompt))
            return '{"status":"COMPLETED","payload":{"summary":"result"},"evidence":["fact-1"]}'

        def checker(prompt):
            calls.append(("checker", prompt))
            self.assertIn("fact-1", prompt)
            return '{"decision":"APPROVED","findings":[],"rationale":"Evidence supports the result."}'

        result = MakerCheckerService(maker, checker).executar(self.request)

        self.assertEqual(result["status"], "APPROVED")
        self.assertEqual(result["checker_result"]["decision"], "APPROVED")
        self.assertEqual([name for name, _ in calls], ["maker", "checker"])
        self.assertIn("<external_data>", calls[0][1])

    def test_invalid_request_does_not_invoke_either_worker(self):
        calls = []
        service = MakerCheckerService(
            maker_worker=lambda prompt: calls.append(("maker", prompt)),
            checker_worker=lambda prompt: calls.append(("checker", prompt)),
        )

        with self.assertRaises(ContractValidationError):
            service.executar({**self.request, "extra": "unexpected"})

        self.assertEqual(calls, [])

    def test_maker_inconclusive_does_not_invoke_checker(self):
        checker_calls = []
        service = MakerCheckerService(
            maker_worker=lambda _: '{"status":"INCONCLUSIVE","payload":{},"evidence":[]}',
            checker_worker=lambda prompt: checker_calls.append(prompt),
        )

        result = service.executar(self.request)

        self.assertEqual(result["status"], "INCONCLUSIVE")
        self.assertIsNone(result["checker_result"])
        self.assertEqual(checker_calls, [])

    def test_invalid_maker_json_fails_without_calling_checker_or_leaking_value(self):
        rejected_value = "sensitive-maker-value"
        checker_calls = []
        service = MakerCheckerService(
            maker_worker=lambda _: f'{{"status":"COMPLETED","payload":"{rejected_value}"',
            checker_worker=lambda prompt: checker_calls.append(prompt),
        )

        with self.assertRaises(ContractValidationError) as raised:
            service.executar(self.request)

        self.assertEqual(raised.exception.code, "invalid_json")
        self.assertNotIn(rejected_value, str(raised.exception))
        self.assertEqual(checker_calls, [])

    def test_invalid_maker_schema_fails_without_calling_checker(self):
        checker_calls = []
        service = MakerCheckerService(
            maker_worker=lambda _: (
                '{"status":"COMPLETED","payload":{},"evidence":[],"extra":"private"}'
            ),
            checker_worker=lambda prompt: checker_calls.append(prompt),
        )

        with self.assertRaises(ContractValidationError):
            service.executar(self.request)

        self.assertEqual(checker_calls, [])

    def test_invalid_checker_decision_fails_closed(self):
        service = MakerCheckerService(
            maker_worker=lambda _: '{"status":"COMPLETED","payload":{},"evidence":[]}',
            checker_worker=lambda _: (
                '{"decision":"MAYBE","findings":[],"rationale":"Not a valid decision."}'
            ),
        )

        with self.assertRaises(ContractValidationError) as raised:
            service.executar(self.request)

        self.assertEqual(raised.exception.code, "schema_invalid")

    def test_valid_checker_rejection_is_returned_as_rejected(self):
        service = MakerCheckerService(
            maker_worker=lambda _: '{"status":"COMPLETED","payload":{},"evidence":[]}',
            checker_worker=lambda _: (
                '{"decision":"REJECTED","findings":["unsupported"],'
                '"rationale":"Evidence is insufficient."}'
            ),
        )

        result = service.executar(self.request)

        self.assertEqual(result["status"], "REJECTED")

    def test_checker_provider_error_propagates(self):
        provider_error = RuntimeError("provider unavailable")
        service = MakerCheckerService(
            maker_worker=lambda _: '{"status":"COMPLETED","payload":{},"evidence":[]}',
            checker_worker=lambda _: (_ for _ in ()).throw(provider_error),
        )

        with self.assertRaisesRegex(RuntimeError, "provider unavailable"):
            service.executar(self.request)


if __name__ == "__main__":
    unittest.main()
