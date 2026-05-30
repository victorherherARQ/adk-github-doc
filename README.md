# ADK 2.0 - Pipeline Automático de Documentación GitHub

Un pipeline de orquestación de agentes IA utilizando **Google ADK 2.0** (open-source) para generar automáticamente `README.md` y `CHANGELOG.md` de repositorios clonados por SSH, con observabilidad completa mediante OpenTelemetry.

---

## 📋 Características

- ✅ **Arquitectura basada en Workflow DAG** - Orquestación determinista con ADK 2.0
- ✅ **Agentes Especializados** - Git Clone Agent + Documentation Generation Agent
- ✅ **LLM Local** - Integración con Ollama (gemma2, qwen2.5-coder, etc.)
- ✅ **Observabilidad Completa** - OpenTelemetry + Prometheus + Grafana
- ✅ **SSH Nativo** - Clonado seguro por SSH con mapeo de volumen
- ✅ **Containerizado** - Docker Compose con orquestación completa
- ✅ **Zero-Config** - Valores por defecto pre-configurados

---

## 🚀 Inicio Rápido

### Requisitos

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git** configurado con SSH
- **Clave SSH** en `~/.ssh/id_rsa` (o equivalente)

### Setup Inicial (5 minutos)

```bash
# 1. Hacer el script ejecutable
chmod +x run.sh

# 2. Configuración inicial (build + start + descargar modelo)
./run.sh setup

# 3. Ejecutar el pipeline
./run.sh run

# 4. Ver logs en tiempo real
./run.sh logs

# 5. Acceder a Grafana
./run.sh grafana
# Usuario: admin
# Contraseña: admin
```

---

## 📁 Estructura del Proyecto

```
adk-github-doc/
├── main.py                           # Entrada principal (Workflow DAG + Agents)
├── Dockerfile                        # Imagen Docker del agente
├── docker-compose.yml                # Orquestación completa
├── requirements.txt                  # Dependencias Python
├── run.sh                           # Script helper para CLI
├── .env.example                     # Plantilla de variables de entorno
├── tools/
│   ├── __init__.py
│   ├── github_tool.py               # Herramienta de clonado SSH
│   └── doc_tool.py                  # Generador de documentación
├── monitoring/
│   ├── otel-collector.yaml          # Configuración OpenTelemetry
│   ├── prometheus.yaml              # Scrape config de Prometheus
│   └── grafana-datasources.yaml     # DataSources de Grafana
└── logs/                            # Directorio de logs (generado)
```

---

## 🏗️ Arquitectura ADK 2.0

### Workflow DAG

```
START
  │
  ├─► git_clone_agent
  │     ├─ Tool: GitHubCloneTool
  │     └─ Output: {repo_path, metadata}
  │
  └─► doc_generation_agent
        ├─ Tool: DocumentationGeneratorTool
        └─ Output: {readme_path, changelog_path}
  │
  END
```

### Agentes

#### 1. **git_clone_agent**
- **Modelo:** gemma2 (Ollama)
- **Herramientas:** `GitHubCloneTool`
- **Tarea:** Clonar repositorio SSH, extraer metadatos
- **Output:** Ruta clonada + metadatos

#### 2. **doc_generation_agent**
- **Modelo:** gemma2 (Ollama)
- **Herramientas:** `DocumentationGeneratorTool`
- **Tarea:** Generar README.md y CHANGELOG.md
- **Output:** Rutas a archivos generados

---

## ⚙️ Comandos Disponibles

```bash
./run.sh help                    # Mostrar ayuda
./run.sh setup                   # Setup inicial (recomendado)
./run.sh build                   # Construir imágenes Docker
./run.sh start                   # Iniciar servicios
./run.sh stop                    # Detener servicios
./run.sh run                     # Ejecutar pipeline
./run.sh logs                    # Ver logs en tiempo real
./run.sh status                  # Ver estado de servicios
./run.sh grafana                 # Abrir Grafana (localhost:3000)
./run.sh model [nombre]          # Descargar modelo Ollama
./run.sh cleanup                 # Limpiar y eliminar volúmenes
```

---

## 📊 Observabilidad

### Grafana Dashboard
- **URL:** http://localhost:3000
- **Usuario:** admin
- **Contraseña:** admin
- **Datasource:** Prometheus

### Prometheus Scrape Config
- **URL:** http://localhost:9090
- **Target:** otel-collector:8889

### OpenTelemetry Collector
- **gRPC Endpoint:** localhost:4317
- **HTTP Endpoint:** localhost:4318
- **Prometheus Export:** localhost:8889

---

## 🔧 Configuración

### Variables de Entorno (`.env`)

```env
# Repositorio a procesar
GITHUB_REPO_SSH=git@github.com:victorherherARQ/poc-mongo-reactivo.git

# Ollama Configuration
OLLAMA_ENDPOINT=http://localhost:11434
MODEL_NAME=gemma2

# OpenTelemetry
OTEL_ENDPOINT=http://localhost:4317

# Paths
WORK_DIR=/tmp/adk-pipeline
LOGS_DIR=./logs

# Logging
LOG_LEVEL=INFO
```

### Modelos Ollama Disponibles

```bash
# Descargar modelo
./run.sh model gemma2              # General purpose (recomendado)
./run.sh model qwen2.5-coder       # Optimizado para código
./run.sh model mistral             # Alto rendimiento
./run.sh model llama2              # Meta Llama 2
./run.sh model neural-chat         # Chatbot especializado
```

---

## 📝 Ejemplo de Uso

### 1. Configuración Inicial
```bash
./run.sh setup
# Esto hará:
# ✓ Build de imágenes Docker
# ✓ Inicia Ollama, Prometheus, Grafana
# ✓ Descarga modelo gemma2
```

### 2. Ejecutar Pipeline
```bash
./run.sh run
# Salida esperada:
# ============================================================
# INICIANDO PIPELINE ADK 2.0 - GENERACIÓN DE DOCUMENTACIÓN
# ============================================================
# 📍 Repositorio: git@github.com:victorherherARQ/poc-mongo-reactivo.git
# 🤖 Modelo: gemma2
# 📊 OpenTelemetry: http://localhost:4317
# 💾 Directorio de trabajo: /tmp/adk-pipeline
# ============================================================
# ▶ Ejecutando workflow...
# ✓ Pipeline ejecutado exitosamente
# ✓ DOCUMENTACIÓN GENERADA
```

### 3. Verificar Archivos Generados
```bash
# Los archivos estará en el volumen adk-work dentro del contenedor
docker-compose exec adk-pipeline ls -la /app/work/poc-mongo-reactivo/
# Salida:
# -rw-r--r-- 1 root root  1234 May 30 23:50 README.md
# -rw-r--r-- 1 root root   567 May 30 23:50 CHANGELOG.md
```

### 4. Monitoreo en Grafana
```bash
./run.sh grafana
# Se abrirá http://localhost:3000 automáticamente
# Visualizar métricas del pipeline y traces de ejecución
```

---

## 🔐 SSH Configuration

### Verificar Configuración SSH

```bash
# Verificar que tienes clave SSH
ls -la ~/.ssh/id_rsa

# Verificar que la clave tiene permisos correctos
chmod 600 ~/.ssh/id_rsa

# Probar conexión SSH con GitHub
ssh -T git@github.com
# Salida esperada: Hi username! You've successfully authenticated...
```

### Mapeo de Volumen SSH

El `docker-compose.yml` mapea automáticamente:

```yaml
volumes:
  - ~/.ssh:/root/.ssh:ro  # SSH read-only
```

Esto permite que el contenedor acceda a tus claves SSH locales de forma segura.

---

## 📈 Observabilidad - Traces y Métricas

### Traces OpenTelemetry

```python
# main.py automaticamente registra:
- Pipeline execution start/end
- Agent activations
- Tool executions
- Error handling
```

### Métricas Prometheus

```
# Disponibles en http://localhost:8889/metrics
- otel_spans_total
- otel_process_*
- ollama_*
```

---

## 🐛 Troubleshooting

### Error: "SSH key not found"
```bash
# Solución:
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
ssh-copy-id -i ~/.ssh/id_rsa git@github.com
./run.sh setup
```

### Error: "Connection refused to Ollama"
```bash
# Solución:
./run.sh status
# Verificar que ollama está RUNNING
docker logs adk-ollama
# Si falta modelo:
./run.sh model gemma2
```

### Error: "Port 11434 already in use"
```bash
# Solución:
lsof -i :11434
kill -9 <PID>
# O cambiar puerto en docker-compose.yml
```

### Ver logs detallados
```bash
./run.sh logs
# O logs específicos de un servicio:
docker-compose logs ollama
docker-compose logs otel-collector
docker-compose logs prometheus
```

---

## 🔍 Verificación Post-Ejecución

```bash
# 1. Verificar archivos generados
docker-compose exec adk-pipeline \
  cat /app/work/poc-mongo-reactivo/README.md

# 2. Verificar CHANGELOG
docker-compose exec adk-pipeline \
  cat /app/work/poc-mongo-reactivo/CHANGELOG.md

# 3. Ver métricas en Grafana
open http://localhost:3000

# 4. Ver traces en Prometheus
open http://localhost:9090
```

---

## 📚 Documentación Referenciada

- **Google ADK:** https://github.com/google-cloud-tools/adk
- **OpenTelemetry:** https://opentelemetry.io/
- **Ollama:** https://ollama.ai/
- **Docker Compose:** https://docs.docker.com/compose/

---

## 📄 Licencia

MIT License - Ver LICENSE para detalles

---

## 🤝 Soporte

Para reportar issues o sugerencias:
- GitHub Issues: [Crear Issue]
- Email: soporte@ejemplo.com

---

**Generado con ❤️ usando Google ADK 2.0**
