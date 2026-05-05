FROM python:3.11-slim

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
