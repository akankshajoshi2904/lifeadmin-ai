
import unittest

from app.agents.router import detect_intent


class TestIntentRouter(unittest.TestCase):

    def test_complete_task(self):
        self.assertEqual(
            detect_intent("Complete my assignment"),
            "complete_task",
        )

    def test_upcoming_tasks(self):
        self.assertEqual(
            detect_intent("Show my upcoming tasks"),
            "upcoming_tasks",
        )

    def test_create_task(self):
        self.assertEqual(
            detect_intent("Create a task to renew insurance"),
            "create_task",
        )

    def test_review_tasks(self):
        self.assertEqual(
            detect_intent("What should I do?"),
            "review_tasks",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
