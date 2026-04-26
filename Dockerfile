FROM python:3.12-slim

WORKDIR /app

COPY backend/docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/auth_service/ .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
