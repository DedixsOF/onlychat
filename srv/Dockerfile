FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements_srv.txt
COPY . .
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]