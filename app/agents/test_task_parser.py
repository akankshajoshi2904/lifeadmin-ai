
import unittest

from app.agents.task_parser import extract_task_title


class TestTaskParser(unittest.TestCase):

    def test_create_task_title(self):
        self.assertEqual(
            extract_task_title(
                "Create a task to submit my project report."
            ),
            "submit my project report",
        )

    def test_add_task_title(self):
        self.assertEqual(
            extract_task_title(
                "Add a task for renewing insurance."
            ),
            "renewing insurance",
        )

    def test_reminder_title(self):
        self.assertEqual(
            extract_task_title(
                "Remind me to pay the electricity bill."
            ),
            "pay the electricity bill",
        )

    def test_finish_assignment_title(self):
        self.assertEqual(
            extract_task_title("Finish my assignment."),
            "Finish my assignment",
        )

    def test_task_title_with_due_date(self):
        self.assertEqual(
            extract_task_title(
                "Create a task to submit my project report by 5 October 2026."
            ),
            "submit my project report",
        )

    def test_reminder_title_with_due_date(self):
        self.assertEqual(
            extract_task_title(
                "Remind me to pay the bill on 12 November 2026."
            ),
            "pay the bill",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
