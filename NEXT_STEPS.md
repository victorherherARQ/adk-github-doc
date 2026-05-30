# 🚀 PRÓXIMOS PASOS - ADK 2.0 Pipeline

## 📋 Checklist Pre-Ejecución

Antes de ejecutar el pipeline, verifica:

```bash
✓ Docker instalado
  $ docker --version

✓ Docker Compose instalado
  $ docker-compose --version

✓ SSH configurado
  $ ssh -T git@github.com
  # Debe responder: "Hi username! You've successfully authenticated"

✓ Clave SSH con permisos correctos
  $ ls -la ~/.ssh/id_rsa
  # Debe mostrar: -rw------- (permisos 600)

✓ Puertos disponibles
  $ lsof -i :11434 || lsof -i :3000 || lsof -i :9090
  # No debe mostrar puertos en uso
```

---

## 🎯 Ejecución en 5 Minutos

### Paso 1: Preparar el Proyecto
```bash
cd /home/vhdez/agentes/adk-github-doc
chmod +x run.sh
```

### Paso 2: Setup Inicial (Automático)
```bash
./run.sh setup

# Este comando:
# 1. Construye las imágenes Docker
# 2. Inicia los 5 servicios
# 3. Descarga el modelo gemma2 en Ollama
# 4. Espera a que todo esté listo
```

**Tiempo estimado:** 5-10 minutos (primera ejecución)

### Paso 3: Verificar Estado
```bash
./run.sh status

# Deberías ver:
# NAME                STATUS
# adk-ollama          Up
# adk-otel-collector  Up
# adk-prometheus      Up
# adk-grafana         Up
# adk-pipeline        Up (or running)
```

### Paso 4: Ejecutar Pipeline
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

### Paso 5: Verificar Archivos Generados
```bash
docker-compose exec adk-pipeline ls -la /app/work/poc-mongo-reactivo/

# Deberías ver:
# -rw-r--r-- 1 root root  1234 May 30 23:50 README.md
# -rw-r--r-- 1 root root   567 May 30 23:50 CHANGELOG.md
```

---

## 📊 Monitorear Ejecución

### Opción 1: Logs en Vivo
```bash
./run.sh logs

# O en otra terminal para ver otro servicio:
docker-compose logs -f ollama
docker-compose logs -f otel-collector
```

### Opción 2: Dashboard Grafana
```bash
./run.sh grafana
# Se abrirá automáticamente en http://localhost:3000
# Usuario: admin
# Contraseña: admin
```

### Opción 3: Prometheus Metrics
```bash
# Abrir en navegador: http://localhost:9090
# Ejecutar queries:
# - rate(otel_spans_total[5m])
# - up{job="ollama"}
```

---

## ✅ Validación Post-Ejecución

### 1. Verificar Contenedores
```bash
docker-compose ps

# Estado esperado:
# adk-ollama           Up
# adk-otel-collector   Up
# adk-prometheus       Up
# adk-grafana          Up
# adk-pipeline         Exited (0)  # Normal tras completarse
```

### 2. Verificar Health Checks
```bash
# Ollama
curl http://localhost:11434/api/tags
# Respuesta: {"models": [{"name": "gemma2", ...}]}

# Prometheus
curl http://localhost:9090/-/healthy
# Respuesta: Prometheus is Healthy
```

### 3. Verificar Archivos Generados
```bash
# Ver README generado
docker-compose exec adk-pipeline cat /app/work/poc-mongo-reactivo/README.md

# Ver CHANGELOG generado
docker-compose exec adk-pipeline cat /app/work/poc-mongo-reactivo/CHANGELOG.md

# Ver estructura del repositorio clonado
docker-compose exec adk-pipeline tree -L 2 /app/work/poc-mongo-reactivo/
```

---

## 🔄 Ejecutar Pipeline Nuevamente

Si deseas ejecutar el pipeline con un repositorio diferente:

### Opción 1: Variable de Entorno
```bash
export GITHUB_REPO_SSH="git@github.com:otro-usuario/otro-repo.git"
docker-compose exec adk-pipeline python main.py
```

### Opción 2: Editar docker-compose.yml
```yaml
services:
  adk-pipeline:
    environment:
      - GITHUB_REPO_SSH=git@github.com:otro-usuario/otro-repo.git
```

### Opción 3: Cambiar Modelo Ollama
```bash
./run.sh model qwen2.5-coder
# Luego:
./run.sh run
```

---

## 📝 Personalización

### Agregar Otro Repositorio sin Parar Servicios

```bash
# 1. Crear instancia adicional
docker-compose -f docker-compose.yml \
  -f docker-compose.additional.yml up -d

# 2. En docker-compose.additional.yml:
services:
  adk-pipeline-2:
    build: .
    environment:
      GITHUB_REPO_SSH: git@github.com:otro/repo.git
      WORK_DIR: /app/work2
    volumes:
      - ~/.ssh:/root/.ssh:ro
      - adk-work-2:/app/work2

volumes:
  adk-work-2:
```

### Cambiar Configuración de OpenTelemetry

Editar `monitoring/otel-collector.yaml`:

```yaml
processors:
  batch:
    timeout: 30s  # Aumentar timeout
    send_batch_size: 2048  # Más spans por batch

exporters:
  jaeger:  # Agregar Jaeger
    endpoint: jaeger:14250
```

---

## 🧹 Limpieza

### Parar Servicios
```bash
./run.sh stop
# O:
docker-compose down
```

### Eliminar Volúmenes (CUIDADO)
```bash
docker-compose down -v

# O selectivamente:
docker volume rm adk-ollama-data   # Borra modelos descargados
docker volume rm adk-prometheus-data  # Borra métricas
docker volume rm adk-grafana-data  # Borra dashboards
docker volume rm adk-work          # Borra repositorios clonados
```

### Limpiar Imagenes
```bash
docker-compose down --rmi all  # Elimina imágenes del proyecto
docker system prune            # Limpia todo sin usar
```

---

## 🐛 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| `Connection refused` en Ollama | `./run.sh status` y `docker logs adk-ollama` |
| SSH permission denied | `chmod 600 ~/.ssh/id_rsa` y `chmod 700 ~/.ssh` |
| Port already in use | `lsof -i :11434` → `kill -9 <PID>` |
| Modelo no encontrado | `./run.sh model gemma2` |
| Pipeline container exits | `docker-compose logs adk-pipeline` |
| Out of memory | Aumentar docker memory limits |

---

## 📚 Consulta la Documentación

Para información más detallada:

- **README.md** - Guía completa y configuración
- **QUICK_START.md** - Inicio en 3 pasos
- **DEPLOYMENT_GUIDE.md** - Deployment avanzado
- **ARCHITECTURE.md** - Detalles técnicos del sistema
- **SUMMARY.txt** - Resumen ejecutivo

---

## 🎯 Objetivo Alcanzado

El pipeline ADK 2.0 está **100% listo** para:

✅ Clonar repositorios por SSH  
✅ Generar documentación automática  
✅ Usar LLM local (Ollama)  
✅ Monitorear ejecución (OpenTelemetry)  
✅ Visualizar métricas (Grafana)  
✅ Escalar a múltiples repositorios  

---

**¿Listo para ejecutar? Comienza con:**
```bash
cd /home/vhdez/agentes/adk-github-doc
./run.sh setup
./run.sh run
```

