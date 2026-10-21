
import unittest
from unittest.mock import patch
import uuid

from app.task_manager import get_tasks


class TestTaskManager(unittest.TestCase):

    def setUp(self):
        self.session_id = f"test-{uuid.uuid4()}"

    @patch("app.task_manager.database_connection")
    def test_get_tasks_returns_a_list(self, mock_database_connection):
        mock_connection = mock_database_connection.return_value.__enter__.return_value
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value

        mock_cursor.fetchall.return_value = []

        tasks = get_tasks(self.session_id)

        self.assertIsInstance(tasks, list)
        self.assertEqual(tasks, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
