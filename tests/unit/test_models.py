from unittest.mock import Mock

import pytest

import taskw.models as mod


def test_Project_completeness():
    manager = Mock()
    manager.tasks.all.return_value = [
        mod.Task(manager, project="aaa", status="pending"),
        mod.Task(manager, project="aaa", status="pending"),
        mod.Task(manager, project="aaa", status="completed"),
        mod.Task(manager, project="aaa", status="completed"),
        mod.Task(manager, project="aaa", status="deleted"),
        mod.Task(manager, project="bbb", status="deleted"),
    ]

    proj_aaa = mod.Project.get(manager, "aaa")
    proj_bbb = mod.Project.get(manager, "bbb")

    assert proj_aaa.completeness() == 0.5
    assert proj_aaa.completeness_percent() == 50

    # no bbb tasks
    assert proj_bbb.completeness() == 1.0
    assert proj_bbb.completeness_percent() == 100


def test_Project_get():
    manager = Mock()
    manager.tasks.all.return_value = [
        mod.Task(manager, project="bbb"),
        mod.Task(manager, project=None),
        mod.Task(manager, project="bbb"),
        mod.Task(manager, project="aaa"),
    ]

    proj_aaa = mod.Project.get(manager, "aaa")
    proj_bbb = mod.Project.get(manager, "bbb")

    assert proj_aaa.name == "aaa"
    assert len(proj_aaa.tasks) == 1
    assert proj_bbb.name == "bbb"
    assert len(proj_bbb.tasks) == 2


def test_Project_all():
    manager = Mock()
    manager.tasks.all.return_value = [
        mod.Task(manager, project="bbb"),
        mod.Task(manager, project=None),
        mod.Task(manager, project="bbb"),
        mod.Task(manager, project="aaa"),
    ]

    projs = mod.Project.all(manager)

    assert len(projs) == 2
    proj_aaa = next(p for p in projs if p.name == "aaa")
    proj_bbb = next(p for p in projs if p.name == "bbb")
    assert len(proj_aaa.tasks) == 1
    assert len(proj_bbb.tasks) == 2


def test_Project_names():
    manager = Mock()
    manager.tasks.all.return_value = [
        mod.Task(manager, project="bbb"),
        mod.Task(manager, project=None),
        mod.Task(manager, project="bbb"),
        mod.Task(manager, project="aaa"),
    ]

    projs = mod.Project.names(manager)

    assert projs == ["aaa", "bbb"]


def test_Tag_names():
    manager = Mock()
    manager.tasks.all.return_value = [
        mod.Task(manager, tags=["aaa"]),
        mod.Task(manager, tags=["bbb", "ccc"]),
        mod.Task(manager, tags=None),
        mod.Task(manager, tags=["ccc"]),
        mod.Task(manager, tags=["aaa", "ddd"]),
    ]

    tags = mod.Tag.names(manager)

    assert tags == ["aaa", "bbb", "ccc", "ddd"]


@pytest.mark.parametrize(
    "search,expected",
    [
        pytest.param("", [], id="empty"),
        pytest.param("  foo\t", ["foo"], id="simple"),
        pytest.param(
            "foo,-bar baz; xxyyz", ["foo", "-bar", "baz", "xxyyz"], id="complex"
        ),
    ],
)
def test_Tag_split(search, expected):
    assert mod.Tag.split(search) == expected


@pytest.mark.parametrize(
    "search,expected",
    [
        pytest.param("", "", id="empty"),
        pytest.param("  foo\t", "+foo", id="simple"),
        pytest.param("foo,-bar baz; xxyyz", "+foo -bar +baz +xxyyz", id="complex"),
    ],
)
def test_Tag_to_query(search, expected):
    assert mod.Tag.to_query(search) == expected


def test_Task_set_status():
    manager = Mock()
    task = mod.Task(manager, status="pending")

    task.set_status(mod.TaskStatus.COMPLETED)

    assert task.completed


@pytest.mark.parametrize(
    "orig,status",
    [
        pytest.param("pending", mod.TaskStatus.PENDING, id="same"),
        pytest.param("deleted", mod.TaskStatus.COMPLETED, id="deleted"),
    ],
)
def test_Task_set_status_error(orig, status):
    manager = Mock()
    task = mod.Task(manager, status=orig)

    with pytest.raises(mod.TaskConflict) as exc_info:
        task.set_status(status)
    assert str(exc_info.value) == "status is not applicable"
