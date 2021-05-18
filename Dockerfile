FROM python:3.9.2-buster

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY --chown=$UID anonym /app/anonym

WORKDIR /app
ENV PYTHONPATH=/app

CMD ["python", "anonym/run.py"]

