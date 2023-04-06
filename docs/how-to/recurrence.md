# How to manage recurring tasks

Recurrence and synchronisation may lead to tasks duplication if not configured
properly. Following [man task-sync]() instructions, **deactivate recurrence in
all but one client** (TaskW client is a good fit).

```conf
# on all but TaskW's taskrc
recurrence=0
```

Then, periodically push new recurring tasks onto server with the following
script. Follow the [docs for synchronisation](docs/how-to/sync.md) to know how
to run a command into TaskW's container.

```bash
task sync  # fetch/push latest updates
task       # create recurring tasks if required
task sync  # push newly created tasks
```

## See also

Taskwarrior [official documentation].


[man task-sync]: https://man.archlinux.org/man/community/task/task-sync.5.en#OPTION_3:_TASKSERVER
[official documentation]: https://taskwarrior.org/docs/recurrence/
