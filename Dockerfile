
FROM python:3.11-slim

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=180
ENV PIP_RETRIES=10
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --retries 10 --timeout 180 -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
