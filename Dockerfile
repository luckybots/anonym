FROM python:3.9.2-buster

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY --chown=$UID anocom /app/anocom
COPY --chown=$UID tengine /app/tengine

WORKDIR /app
ENV PYTHONPATH=/app

CMD ["python", "anocom/run.py"]

