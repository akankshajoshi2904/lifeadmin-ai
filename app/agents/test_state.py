
import unittest

from app.agents.state import AgentState


class TestAgentState(unittest.TestCase):

    def setUp(self):
        self.state = AgentState(
            user_request="What do I need to take care of?",
            intent="review_tasks",
            current_step="Planning tasks",
        )

    def test_initial_state_values(self):
        self.assertEqual(
            self.state.user_request,
            "What do I need to take care of?",
        )
        self.assertEqual(self.state.intent, "review_tasks")
        self.assertEqual(self.state.current_step, "Planning tasks")

    def test_tasks_can_be_stored(self):
        self.state.tasks = [
            {
                "title": "Renew Insurance",
                "due_date": "14 October 2026",
                "priority": "High",
            }
        ]

        self.assertEqual(len(self.state.tasks), 1)
        self.assertEqual(
            self.state.tasks[0]["title"],
            "Renew Insurance",
        )

    def test_plan_can_be_stored(self):
        self.state.plan = ["Renew Insurance"]

        self.assertEqual(self.state.plan, ["Renew Insurance"])

    def test_approval_values_can_be_stored(self):
        self.state.approval_required = True
        self.state.approved = False

        self.assertTrue(self.state.approval_required)
        self.assertFalse(self.state.approved)

    def test_response_can_be_stored(self):
        self.state.response = (
            "Your next action is to renew your insurance."
        )

        self.assertEqual(
            self.state.response,
            "Your next action is to renew your insurance.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
