FROM python:3.11-slim

# Metadata
LABEL maintainer="ADK Pipeline"
LABEL description="Pipeline de generación automática de documentación con ADK 2.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV WORK_DIR=/app/work
ENV OLLAMA_ENDPOINT=http://ollama:11434

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ssh-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY main.py .
COPY tools/ ./tools/

# Crear directorio de trabajo para repositorios
RUN mkdir -p ${WORK_DIR} && chmod 755 ${WORK_DIR}

# Configurar SSH (volumen en tiempo de ejecución)
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["python", "main.py"]
