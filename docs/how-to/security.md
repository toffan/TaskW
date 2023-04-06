# How to securely deploy

TaskW is only a taskwarrior frontend. There isn't any builtin security feature
such as confidentiality or integrity. It is strongly advised to deploy TaskW
behind a security layer.

In your production deployment please make sure that:
1. no one can directly access TaskW without going thought the security layer
2. the security layer enforces authentication
3. the security layer enforces encryption

## Example, Traefik

*Disclaimer: this is an example of secured deployment that by no mean is
universal. Copy and adapt with caution.*

```yaml
version: '3.7'

services:
  revproxy:
    image: traefik:v2.9
    command:
      # Ref: https://docs.traefik.io/reference/static-configuration/cli/
      # Enable docker provider
      - --providers.docker=true
      - --providers.docker.swarmmode=true
        # do not expose containers unless explicitly told so
      - --providers.docker.exposedbydefault=false
      # Entrypoints
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      # Let's Encrypt config for certificate creation
      - --certificatesResolvers.le.acme.email=MY_EMAIL
        # used during the challenge
      - --certificatesResolvers.le.acme.httpChallenge.entryPoint=web
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
    secrets:
      - source: htpasswd
        target: htpasswd
        mode: 0444
    deploy:
      labels:
        # Traefik managed
        - traefik.enable=true
        # Redirect http to https
          # listen on *:80
        - traefik.http.routers.webinsecure.entrypoints=web
        - traefik.http.routers.webinsecure.rule=HostRegexp(`{host:.+}`)

        # Redirect http to https
        - traefik.http.routers.webinsecure.middlewares=redirect-to-https
        - traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https
        - traefik.http.middlewares.redirect-to-https.redirectscheme.permanent=true

          # authentification
        - traefik.http.middlewares.auth.basicauth.usersFile=/run/secrets/htpasswd
        - traefik.http.middlewares.auth.basicauth.removeheader=true
        - traefik.http.routers.traefik.middlewares=auth

          # dummy service for Swarm port detection. The port can be any valid integer value.
          # cf. https://docs.traefik.io/v2.0/operations/dashboard/
        - traefik.http.services.dummy.loadbalancer.server.port=9999

  taskw:
    image: taskw:0.0.2
    volumes:
      - 'taskw-data:/home/app/taskdata'
    init: true
    configs:
      - source: taskw_taskrc
        target: /home/app/taskrc
        mode: 0444
    deploy:
      labels:
        # Traefik managed
        - traefik.enable=true
        - traefik.http.routers.taskw.rule=Host(`MY_TASK_DOMAIN`)
          # service listen on port 80
        - traefik.http.services.taskw.loadbalancer.server.port=80

        # Accept and force https with letsencrypt
        - traefik.http.routers.taskw.entrypoints=websecure
        - traefik.http.routers.taskw.tls=true
        - traefik.http.routers.taskw.tls.certresolver=le

        # Basic Auth
        - traefik.http.routers.taskw.middlewares=auth

configs:
  taskw_taskrc:
    file: ./taskrc

volumes:
  taskw-data:

secrets:
  htpasswd:
    file: ./htpasswd
```
