
import unittest
from unittest.mock import patch

from app.agents.state import AgentState
from app.agents.workflow import lifeadmin_agent


class TestLifeAdminWorkflow(unittest.TestCase):

    def test_workflow_detects_complete_task_intent(self):
        state = AgentState(
            user_request="Complete my next task.",
            approved=False,
        )

        result = lifeadmin_agent.invoke(state)

        self.assertEqual(result["intent"], "complete_task")

    def test_workflow_requires_approval(self):
        state = AgentState(
            user_request="Complete my next task.",
            approved=False,
        )

        result = lifeadmin_agent.invoke(state)

        self.assertTrue(result["approval_required"])
        self.assertFalse(result["approved"])

    def test_workflow_returns_plan_and_response(self):
        state = AgentState(
            user_request="Complete my next task.",
            approved=False,
        )

        result = lifeadmin_agent.invoke(state)

        self.assertIsInstance(result["plan"], list)
        self.assertIsInstance(result["tasks"], list)
        self.assertIsInstance(result["response"], str)
        self.assertTrue(result["response"])

    @patch("app.agents.workflow.get_memory")
    def test_named_task_is_selected(self, mock_get_memory):
        mock_get_memory.return_value = [
            {
                "id": 9,
                "title": "test LifeAdmin AI",
                "due_date": "20 October 2026",
                "priority": "Medium",
                "status": "Pending",
            },
            {
                "id": 4,
                "title": "submit my project report",
                "due_date": "10 October 2026",
                "priority": "Medium",
                "status": "Pending",
            },
        ]

        state = AgentState(
            user_request="Complete my task named test LifeAdmin AI.",
            approved=False,
        )

        result = lifeadmin_agent.invoke(state)

        self.assertEqual(result["intent"], "complete_task")
        self.assertEqual(result["plan"], ["test LifeAdmin AI"])
        self.assertTrue(result["approval_required"])
        self.assertFalse(result["approved"])
        self.assertIn("test LifeAdmin AI", result["response"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
