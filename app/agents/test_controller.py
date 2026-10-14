
import unittest

from app.agents.controller import (
    prepare_request,
    approve_request,
    reject_request,
)


class TestController(unittest.TestCase):

    def setUp(self):
        self.request = (
            "Create a task to review the LifeAdmin project "
            "by 20 October 2026."
        )

    def test_prepare_request_requires_approval(self):
        state = prepare_request(self.request)

        self.assertTrue(state["approval_required"])
        self.assertFalse(state["approved"])

    def test_approve_request(self):
        state = prepare_request(self.request)

        approved_state = approve_request(state)

        self.assertTrue(approved_state.approved)
        self.assertEqual(
            approved_state.current_step,
            "Action approved",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
