FROM python:3.10-slim

# Use /app instead of root (/)
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Corrected command (no --app-dir needed now!)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]