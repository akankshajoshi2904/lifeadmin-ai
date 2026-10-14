
import unittest

from app.agents.state import AgentState
from app.agents.approval import approve_action, reject_action


class TestApproval(unittest.TestCase):

    def test_approve_action(self):
        state = AgentState(
            user_request="Create a task to submit my project report.",
            approval_required=True,
            approved=False,
        )

        result = approve_action(state)

        self.assertTrue(result.approved)
        self.assertEqual(result.current_step, "Action approved")

    def test_reject_action(self):
        state = AgentState(
            user_request="Create a task to submit my project report.",
            approval_required=True,
            approved=False,
        )

        result = reject_action(state)

        self.assertFalse(result.approved)
        self.assertFalse(result.approval_required)
        self.assertEqual(result.current_step, "Action rejected")


if __name__ == "__main__":
    unittest.main(verbosity=2)
