import enum
import re
from collections.abc import Collection

from tasklib import Task
from tasklib import TaskWarrior

from .utils import groupby


class TaskPriority(enum.Enum):
    LOW = "L"
    MEDIUM = "M"
    HIGH = "H"


class Project:
    def __init__(self, name: str, tasks: Collection[Task]):
        assert name
        assert all(t["project"] == name for t in tasks)

        self.name = name
        self.tasks = tasks

    def completeness(self) -> float:
        total_cnt = sum(1 for t in self.tasks if t["status"] != "deleted")
        if total_cnt == 0:
            return 1.0
        completed_cnt = sum(1 for t in self.tasks if t["status"] == "completed")
        return completed_cnt / total_cnt

    def completeness_percent(self) -> int:
        return int(self.completeness() * 100)

    def pending(self):
        return [t for t in self.tasks if t["status"] == "pending"]

    @classmethod
    def get(cls, manager: TaskWarrior, name: str):
        return Project(name, [t for t in manager.tasks.all() if t["project"] == name])

    @classmethod
    def all(cls, manager: TaskWarrior):
        return [
            Project(name, tasks)
            for name, tasks in groupby(
                manager.tasks.all(), lambda t: t["project"]
            ).items()
        ]

    @classmethod
    def filter(cls, manager: TaskWarrior, predicate):
        return [p for p in cls.all(manager) if predicate(p)]

    @classmethod
    def names(cls, manager: TaskWarrior) -> list[str]:
        return sorted({t["project"] for t in manager.tasks.all() if t["project"]})


class Tag:
    @classmethod
    def names(cls, manager: TaskWarrior):
        tags = set()
        for task in manager.tasks.all():
            if task["tags"]:
                tags.update(task["tags"])
        return sorted(tags)

    @staticmethod
    def split(s: str) -> list[str]:
        """Split a string in tags that may start with a '-'

        >>> split("foo,-bar baz; xxyyz")
        ["foo", "-bar", "baz", "xxyyz"]
        """
        return re.findall(r"-?\w+", s)

    @staticmethod
    def to_query(s: str) -> str:
        """Split and partition a string into included and excluded tags

        >>> parse_tags("foo,-bar baz; xxyyz")
        "+foo -bar +baz +xxyyz"
        """
        return " ".join(t if t[0] == "-" else "+" + t for t in Tag.split(s))


class TaskStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    DELETED = "deleted"


class TaskConflict(Exception):
    def __init__(self, msg: str, ctx: dict = {}):
        self.msg = msg
        self.ctx = ctx

    def __str__(self) -> str:
        return self.msg


def Task_set_status(task: Task, status: TaskStatus):
    if task["status"] == status.value or (
        task.deleted and status == TaskStatus.COMPLETED
    ):
        raise TaskConflict(
            msg="status is not applicable",
            ctx={"task": {"status": task["status"]}},
        )

    task["status"] = status.value


Task.set_status = Task_set_status
Task.TaskConflict = TaskConflict
