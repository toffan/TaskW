# How to sync with a remote taskserver

First, deploy a taskserver following [official documentation][taskserver-setup].
Generate a couple of keys for the repository. Share the CA cert, the client key
and the client cert using either volumes or secrets (not described here).
Configure TaskW's taskrc file like any client (see [man task-sync]()).

## Option 1. with cron

Make sure your server has a cron server up and running. Then, as root user add
a periodic task that exec a sync from the container (replace `PATH_DOCKER_COMPOSE`
with the path to docker-compose.yml). 
```console
# crontab -e
  ## Add the following lines
  # Sync TaskW state every 15min
  15 * * * * docker-compose -f PATH_DOCKER_COMPOSE exec -T --env TASKRC=taskrc taskw task sync
```

Or if TaskW is deployed as a docker service
```cron
15 * * * * /bin/sh /root/.local/bin/taskw-sync.sh
```

```bash
# /root/.local/bin/taskw-sync.sh
docker exec --env TASKRC=taskrc $(docker ps -q -f name=SERVICE_NAME) task sync
```

## Option 2. from web

TaskW performs a sync when hit on `POST /sync`. Use any mean to periodically
send a request on this endpoint.


[taskserver-setup]: https://gothenburgbitfactory.github.io/taskserver-setup/
[man task-sync]: https://man.archlinux.org/man/community/task/task-sync.5.en#OPTION_3:_TASKSERVER
