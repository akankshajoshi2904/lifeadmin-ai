
import unittest

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
