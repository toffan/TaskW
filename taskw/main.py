import enum
import os
from urllib.parse import SplitResult
from urllib.parse import urlencode

from fastapi import FastAPI
from fastapi import Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import UUID4
from tasklib import TaskWarrior

from .models import Project
from .models import Tag
from .models import Task
from .models import TaskPriority
from .models import TaskStatus
from .utils import hrdate
from .utils import urlb64decode
from .utils import urlb64encode


def make_tag_url(request: Request, tag: str) -> str:
    params = {}

    if tab := request.query_params.get("tab"):
        params["tab"] = tab

    if tags := request.query_params.get("tags"):
        tags = set(Tag.split(tags))
        tags.add(tag)
        params["tags"] = ",".join(tags)
    else:
        params["tags"] = tag

    components = SplitResult(
        scheme="", netloc="", path="/tasks", query=urlencode(params), fragment=""
    )
    return components.geturl()


app = FastAPI(title="taskw", debug=True)

app.mount("/static", StaticFiles(directory="website/static"), name="static")

templates = Jinja2Templates(directory="website/templates")
templates.env.filters["hrdate"] = hrdate
templates.env.filters["urlb64encode"] = urlb64encode
templates.env.filters["urlb64decode"] = urlb64decode
templates.env.globals["make_tag_url"] = make_tag_url

manager = TaskWarrior(
    data_location=os.getenv("TASKDATA", "~/taskdata"),
    taskrc_location=os.getenv("TASKRC", "~/taskrc"),
)


class TaskTab(enum.Enum):
    PENDING = "pending"
    WAITING = "waiting"
    COMPLETED = "completed"
    DELETED = "deleted"
    # TODAY = "today"  # TODO
    # WEEK = "week"  # TODO

    def get_filters(self):
        filters = {
            "pending": {"status": "pending"},
            "waiting": {"status": "waiting"},
            "completed": {"status": "completed"},
            "deleted": {"status": "deleted"},
            # "today": ...,
            # "deleted": ...,
        }
        return filters[self.value]

    def get_sort_key(self):
        sort_key = {
            "pending": (lambda t: t["urgency"]),
            "waiting": (lambda t: t["wait"]),
            "completed": (lambda t: t["end"]),
            "deleted": (lambda t: t["end"]),
            # "today": ...,
            # "deleted": ...,
        }
        return sort_key[self.value]


class TaskView(enum.IntFlag):
    PROJECT = enum.auto()
    COMPLETION = enum.auto()
    EDITION = enum.auto()
    HIDE = enum.auto()


templates.env.globals["TaskView"] = TaskView


@app.get("/")
def root():
    return RedirectResponse(url="/tasks")


@app.post("/sync")
def sync(request: Request):
    manager.sync()
    return Response(status_code=200)


#   TASKS   ###################################################################


@app.get("/tasks", response_class=HTMLResponse)
def home(
    request: Request,
    tab: TaskTab = TaskTab.PENDING,
    tags: str = "",
):
    if request.headers.get("HX-Request"):
        return task_list(request, tab, tags)
    else:
        response = templates.TemplateResponse(
            "tasks/home.html",
            {
                "request": request,
                "tab": tab.value,
                "tags": tags,
            },
        )
        return response


def task_list(
    request: Request,
    tab: TaskTab = TaskTab.PENDING,
    tags: str = "",
):
    if tags:
        query = Tag.to_query(tags)
        filter = tab.get_filters()
        tasks = manager.tasks.filter(query, **filter)
    else:
        filter = tab.get_filters()
        tasks = manager.tasks.filter(**filter)

    tasks = sorted(tasks, key=tab.get_sort_key(), reverse=True)

    view = TaskView.PROJECT | TaskView.EDITION
    if tab == TaskTab.WAITING:
        view |= TaskView.HIDE
    if tab in [TaskTab.COMPLETED, TaskTab.DELETED]:
        view |= TaskView.COMPLETION

    response = templates.TemplateResponse(
        "tasks/_tabs.html",
        {
            "request": request,
            "tasks": tasks,
            "tags": tags,
            "view": view,
            "tab": tab.value,
        },
    )
    return response


@app.get("/tasks/new", response_class=HTMLResponse)
def task_new(
    request: Request,
    project: str | None = None,
):
    project = urlb64decode(project) if project else ""
    list_projects = Project.names(manager)
    list_tags = Tag.names(manager)

    response = templates.TemplateResponse(
        "tasks/_new.html",
        {
            "request": request,
            "project": project,
            "list_projects": list_projects,
            "list_tags": list_tags,
        },
    )
    return response


@app.post("/tasks", response_class=HTMLResponse)
def task_create(
    request: Request,
    description: str = Form(...),
    project: str | None = Form(None),
    due: str | None = Form(None),
    wait: str | None = Form(None),
    priority: TaskPriority | None = Form(None),
    tags: str = Form(""),
    view: int = Form(...),
):
    if priority:
        priority = priority.value
    tagsl = Tag.split(tags)

    task = Task(
        manager,
        description=description,
        project=project,
        due=due,
        wait=wait,
        priority=priority,
        tags=tagsl,
    )
    task.save()

    response = templates.TemplateResponse(
        "tasks/_item.html",
        {
            "request": request,
            "task": task,
            "view": TaskView(view),
        },
        status_code=201,
    )
    return response


@app.get("/tasks/{uuid}", response_class=HTMLResponse)
def task_get(request: Request, uuid: UUID4):
    try:
        task = manager.get_task(str(uuid))
    except Task.DoesNotExist:
        return Response(status_code=404)

    list_projects = Project.names(manager)
    list_tags = Tag.names(manager)

    response = templates.TemplateResponse(
        "tasks/details.html",
        {
            "request": request,
            "task": task,
            "list_projects": list_projects,
            "list_tags": list_tags,
        },
    )
    return response


@app.patch("/tasks/{uuid}", response_class=HTMLResponse)
def task_patch(
    request: Request,
    uuid: UUID4,
    status: TaskStatus = Form(...),
    view: int = Form(...),
):
    task = manager.get_task(str(uuid))

    try:
        task.set_status(status)
        task.save()
    except Task.TaskConflict as e:
        return JSONResponse(
            {
                "detail": [
                    {
                        "loc": ["query", "status"],
                        "msg": e.msg,
                        "type": "conflict",
                        "ctx": e.ctx,
                    }
                ]
            },
            status_code=409,
        )

    response = templates.TemplateResponse(
        "tasks/_item.html",
        {
            "request": request,
            "task": task,
            "view": TaskView(view),
        },
        status_code=200,
    )
    return response


@app.put("/tasks/{uuid}")
def task_save(
    request: Request,
    uuid: UUID4,
    description: str = Form(...),
    project: str | None = Form(None),
    due: str | None = Form(None),
    wait: str | None = Form(None),
    priority: TaskPriority | None = Form(None),
    tags: str = Form(""),
    status: TaskStatus | None = Form(None),
):
    if priority:
        priority = priority.value
    tagsl = Tag.split(tags)

    task = manager.get_task(str(uuid))

    task["description"] = description
    task["project"] = project
    task["due"] = due
    task["wait"] = wait
    task["priority"] = priority
    task["tags"] = tagsl

    if status is not None:
        try:
            task.set_status(status)
        except Task.TaskConflict as e:
            return JSONResponse(
                {
                    "detail": [
                        {
                            "loc": ["query", "status"],
                            "msg": e.msg,
                            "type": "conflict",
                            "ctx": e.ctx,
                        }
                    ]
                },
                status_code=409,
            )

    task.save()

    dest = request.headers.get("x-referer", "/tasks")
    headers = {"HX-Redirect": dest}
    return Response(status_code=200, headers=headers)


#   ANNOTATIONS   #############################################################


@app.post("/tasks/{uuid}/annotations", response_class=HTMLResponse)
def annotation_create(request: Request, uuid: UUID4, annotation: str = Form(...)):
    task = manager.get_task(str(uuid))
    task.add_annotation(annotation)
    anno = task["annotations"][-1]
    task.save()

    response = templates.TemplateResponse(
        "annotations/_item.html",
        {
            "request": request,
            "task": task,
            "anno": anno,
        },
        status_code=201,
    )
    return response


@app.get("/tasks/{uuid}/annotations", response_class=HTMLResponse)
def annotation_list(request: Request, uuid: UUID4):
    task = manager.get_task(str(uuid))
    response = templates.TemplateResponse(
        "tasks/_annotations.html",
        {
            "request": request,
            "task": task,
        },
    )
    return response


@app.delete("/tasks/{uuid}/annotations/{annotation64}", response_class=HTMLResponse)
def annotation_delete(request: Request, uuid: UUID4, annotation64: str):
    task = manager.get_task(str(uuid))
    task.remove_annotation(urlb64decode(annotation64))
    task.save()

    return Response(status_code=200)


#   PROJECTS   ################################################################


@app.get("/projects", response_class=HTMLResponse)
def project_list(request: Request):
    projects = Project.filter(manager, lambda p: p.completeness() < 1.0)

    response = templates.TemplateResponse(
        "projects/list.html",
        {
            "request": request,
            "projects": projects,
            "view": TaskView(0),
        },
    )
    return response


@app.get("/projects/{project64}", response_class=HTMLResponse)
def project_get(request: Request, project64: str):
    name = urlb64decode(project64)
    project = Project.get(manager, name)

    response = templates.TemplateResponse(
        "projects/details.html",
        {
            "request": request,
            "project": project,
            "view": TaskView.COMPLETION | TaskView.EDITION | TaskView.HIDE,
        },
    )
    return response
