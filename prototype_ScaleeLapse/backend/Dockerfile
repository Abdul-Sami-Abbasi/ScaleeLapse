FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend backend
COPY ai ai
COPY models models
EXPOSE 8000
CMD ["sh","-c","python backend/manage.py migrate && python -m waitress --listen=0.0.0.0:8000 backend.config.wsgi:application"]
