
import unittest

from app.task_manager import (
    create_tasks_table,
    add_task,
    get_tasks,
)


class TestTaskManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        create_tasks_table()

    def test_get_tasks_returns_a_list(self):
        tasks = get_tasks()
        self.assertIsInstance(tasks, list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
