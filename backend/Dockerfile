FROM python:3.9-slim
WORKDIR /app

# 1) Dependencias del SO para TensorFlow
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2) Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copiar código y assets
COPY . .
RUN mkdir -p data models

# 4) Arrancar la API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
