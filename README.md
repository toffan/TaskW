# TaskW

TaskW is yet another taskwarrior web wrapper. It displays a convenient web UI
above a local taskwarrior folder that can easily manipulated from any web
browser (desktop or mobile).

**Features**
- List all pending tasks
- Easily edit a task in its main characteristics
- List all projects and their pending tasks
- Search by tags
- Can synchronize with a remote taskwarrior-server (see [documentation](TODO))
- Is mobile friendly

## Getting started
### Deployment

With docker-compose (recommended)
```console
$ sudo docker-compose build taskw
$ sudo docker-compose up -d taskw
```

Or with docker cli
```console
$ sudo docker build -t taskw:latest .
$ sudo docker run -p 80:80 taskw:latest
```

### Configuration

Configuration is split in 2, a *taskrc* file to configure taskwarrior and a
*taskw.toml* file to configure the taskw web app. The distinction between the 2
can be blurry that's why it is recommended to start from the given examples.
```console
$ $EDITOR taskrc taskw.toml
$ # re-deploy and use the configuration
$ sudo docker run -p 80:80 -v $PWD/taskrc:/home/app:ro -v $PWD/taskw.toml:/home/app:ro taskw:latest
```
## FAQ

**Can I sync my local taskwarrior client with it?**

No. TaskW is a frontend to a taskwarrior client, not a taskwarrior server. If
you want to synchronize several clients you must deploy a taskwarrior server by
yourself.

```
   LAPTOP / PC                                 SERVER
┌─  ──  ──  ──  ─┐           ┌─  ──  ──  ──  ──  ──  ──  ──  ──  ──  ──  ──  ──  ──  ─┐
  ┌───────────┐      HTTP       ┌───────┐     ┌───────────┐           ┌─────────────┐
│ │  browser  ├──┼───────────┼──┤ TaskW ├─────┤ TASKDATA  │           │             │ │
  └───────────┘                 └───────┘     ├─ ─ ─ ─ ─ ─┤ TASK SYNC │ taskwarrior │
│ ┌───────────┐  │           │                │ task CLI  ├───────────┤             │ │
  │ TASKDATA  │                               └───────────┘           │   server    │
│ ├─ ─ ─ ─ ─ ─┤  │ TASK SYNC │                                        │             │ │
  │ task CLI  ├───────────────────────────────────────────────────────┤             │
│ └───────────┘  │           │                                        └─────────────┘ │
└─  ──  ──  ──  ─┘           └─  ──  ──  ──  ──  ──  ──  ──  ──  ──  ──  ──  ──  ──  ─┘
```

**Doesn't TaskW looks a bit like [taskwarrior-web]?**

It definitely does. I've mostly tried to reproduce taskwarrior-web's UX in
TaskW. I also added 2 features that were not in taskwarrior-web, TaskW lets you
filter tasks by tags and can force a sync with a taskwarrior server. However,
TaskW does not let you sort tasks, what taskwarrior-web does. 

**Why not contribute to [taskwarrior-web] instead?**

Because taskwarrior-web is developed in Ruby and jquery both of which I'm
absolutely not comfortable with. On the other hand TaskW is developed in python
and htmx.

**Is TaskW good?**

It is good enough for me and hopefully for you too.


[taskwarrior-web]: https://github.com/theunraveler/taskwarrior-web
