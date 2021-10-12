FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY venv /app

CMD ["python", "app.py"]
