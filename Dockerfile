FROM python:3.11-alpine

RUN apk add --no-cache task

RUN adduser -D app
USER app
WORKDIR /home/app

COPY --chown=app requirements/prod.txt requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

ADD \
    # Not available yet
    # --checksum=sha256:3a45b8620b4cf25eceb3f4c90f319a8fde139f857c410a201f6696f0db2eb593
    --chown=app https://use.fontawesome.com/releases/v6.2.1/fontawesome-free-6.2.1-web.zip /tmp/
RUN mkdir -p website/static/ \
    && unzip /tmp/fontawesome-free-6.2.1-web.zip -d website/static/

COPY --chown=app taskw taskw/
COPY --chown=app website website/
COPY --chown=app taskrc taskrc

RUN mkdir taskdata

VOLUME /home/app/taskdata
EXPOSE 80
CMD python -m uvicorn taskw.main:app --host 0.0.0.0 --port 80
