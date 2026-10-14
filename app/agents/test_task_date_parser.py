
import unittest

from app.agents.task_date_parser import extract_due_date


class TestTaskDateParser(unittest.TestCase):

    def test_extract_date_with_by_keyword(self):
        self.assertEqual(
            extract_due_date(
                "Create a task to submit my report by 5 October 2026."
            ),
            "5 October 2026",
        )

    def test_extract_date_with_on_keyword(self):
        self.assertEqual(
            extract_due_date(
                "Remind me to pay the bill on 12 November 2026."
            ),
            "12 November 2026",
        )

    def test_request_without_due_date(self):
        self.assertIsNone(
            extract_due_date(
                "Create a task to prepare for my exam."
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
