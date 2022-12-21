# CONTRIBUTING

## Run a dev server

Download fontawesome free and unpack the archive under *website/static/* (only once)
```console
$ cd website/static/
$ wget https://use.fontawesome.com/releases/v6.2.1/fontawesome-free-6.2.1-web.zip
$ sha256sum -c CHECKSUMS.txt
$ unzip fontawesome-free-6.2.1-web.zip
```

From the *taskw/* directory
```console
$ TASKRC=taskrc poetry run uvicorn taskw.main:app --reload
```

## Repository policy

Code is formatted with *reorder-python-imports* and *black*.

To contribute, it is recommended to assign an issue to you, then open a *Pull
Request* into the *main* branch. Hopefully it will soon be reviewed and merged.
