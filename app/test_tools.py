
import unittest

from app.tools.task_tools import (
    create_task_tool,
    list_tasks_tool,
    complete_task_tool,
)


class TestTaskTools(unittest.TestCase):

    def test_create_task_tool_is_available(self):
        self.assertTrue(callable(create_task_tool))

    def test_list_tasks_tool_is_available(self):
        self.assertTrue(callable(list_tasks_tool))

    def test_complete_task_tool_is_available(self):
        self.assertTrue(callable(complete_task_tool))


if __name__ == "__main__":
    unittest.main(verbosity=2)
