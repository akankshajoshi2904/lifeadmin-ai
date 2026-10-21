
import unittest
from unittest.mock import patch

from app.agents.state import AgentState
from app.agents.workflow import lifeadmin_agent


class TestLifeAdminWorkflow(unittest.TestCase):
    def setUp(self):
        self.session_id = "workflow-test-session"

        self.tasks = [
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

        self.memory_patcher = patch(
            "app.agents.workflow.get_memory",
            return_value=self.tasks,
        )
        self.mock_get_memory = self.memory_patcher.start()
        self.addCleanup(self.memory_patcher.stop)

    def run_request(self, request):
        state = AgentState(
            user_request=request,
            session_id=self.session_id,
            approved=False,
        )
        return lifeadmin_agent.invoke(state)

    def test_workflow_detects_complete_task_intent(self):
        result = self.run_request(
            "Complete my task named test LifeAdmin AI."
        )
        self.assertEqual(result["intent"], "complete_task")

    def test_workflow_requires_approval(self):
        result = self.run_request(
            "Complete my task named test LifeAdmin AI."
        )
        self.assertTrue(result["approval_required"])
        self.assertFalse(result["approved"])
        self.assertEqual(result["selected_task_id"], 9)

    def test_workflow_returns_plan_and_response(self):
        result = self.run_request(
            "Complete my task named test LifeAdmin AI."
        )
        self.assertIsInstance(result["plan"], list)
        self.assertIsInstance(result["tasks"], list)
        self.assertIsInstance(result["response"], str)
        self.assertTrue(result["response"])
        self.assertEqual(
            result["plan"],
            ["Complete: test LifeAdmin AI"],
        )

    def test_named_task_is_selected(self):
        result = self.run_request(
            "Complete my task named test LifeAdmin AI."
        )
        self.assertEqual(result["intent"], "complete_task")
        self.assertEqual(result["selected_task_id"], 9)
        self.assertEqual(
            result["plan"],
            ["Complete: test LifeAdmin AI"],
        )
        self.assertTrue(result["approval_required"])
        self.assertFalse(result["approved"])
        self.assertIn(
            "test LifeAdmin AI",
            result["selected_task"]["title"],
        )

    def test_ambiguous_task_requires_clarification(self):
        self.tasks.append(
            {
                "id": 10,
                "title": "test LifeAdmin AI backup",
                "due_date": None,
                "priority": "Low",
                "status": "Pending",
            }
        )
        result = self.run_request(
            "Complete my test LifeAdmin AI task."
        )
        self.assertTrue(result["clarification_required"])
        self.assertFalse(result["approval_required"])
        self.assertIsNone(result["selected_task_id"])

    def test_generic_complete_request_offers_pending_task_choices(self):
        result = self.run_request("Complete my task")

        self.assertEqual(result["intent"], "complete_task")
        self.assertTrue(result["clarification_required"])
        self.assertFalse(result["approval_required"])
        self.assertFalse(result["approved"])
        self.assertIsNone(result["selected_task_id"])

        candidate_titles = [
            task["title"] for task in result["candidate_tasks"]
        ]

        self.assertCountEqual(
            candidate_titles,
            [
                "test LifeAdmin AI",
                "submit my project report",
            ],
        )
        self.assertIn("Reply with the number", result["response"])

    def test_generic_complete_request_excludes_completed_tasks(self):
        self.tasks.append(
            {
                "id": 12,
                "title": "Already completed task",
                "due_date": None,
                "priority": "Low",
                "status": "Completed",
            }
        )

        result = self.run_request("Complete my task")
        candidate_titles = [
            task["title"] for task in result["candidate_tasks"]
        ]

        self.assertNotIn("Already completed task", candidate_titles)
        self.assertFalse(result["approval_required"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
