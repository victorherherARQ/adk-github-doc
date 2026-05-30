# 📦 DEPLOYMENT GUIDE - ADK 2.0 Pipeline

## Verificación Pre-Deployment

### 1. Requisitos del Sistema
```bash
# Verificar Docker
docker --version
# Esperado: Docker version 20.10+

# Verificar Docker Compose
docker-compose --version
# Esperado: Docker Compose version 2.0+

# Verificar Git
git --version
# Esperado: git version 2.0+
```

### 2. Configuración SSH
```bash
# Verificar clave SSH
ls -la ~/.ssh/id_rsa
# Esperado: -rw------- 1 user user 3434 ...

# Probar conexión GitHub
ssh -T git@github.com
# Esperado: Hi username! You've successfully authenticated...

# Configurar permisos SSH
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh
```

### 3. Puertos Disponibles
```bash
# Verificar que los puertos estén disponibles
lsof -i :11434 || echo "✓ Puerto 11434 disponible"
lsof -i :3000 || echo "✓ Puerto 3000 disponible"
lsof -i :9090 || echo "✓ Puerto 9090 disponible"
lsof -i :4317 || echo "✓ Puerto 4317 disponible"
```

---

## Pasos de Deployment

### OPCIÓN 1: Usando Script (Recomendado)

```bash
# 1. Clonar o descargar el proyecto
cd adk-github-doc

# 2. Hacer el script ejecutable
chmod +x run.sh

# 3. Ejecutar setup (automático)
./run.sh setup
# Esto toma ~5-10 minutos la primera vez

# 4. Verificar que servicios están corriendo
./run.sh status

# 5. Ejecutar pipeline
./run.sh run
```

### OPCIÓN 2: Usando Makefile

```bash
# 1. Configurar proyecto
cd adk-github-doc

# 2. Ejecutar setup
make setup

# 3. Verificar status
make status

# 4. Ejecutar pipeline
make run
```

### OPCIÓN 3: Manual con Docker Compose

```bash
# 1. Build
docker-compose build

# 2. Start servicios
docker-compose up -d

# 3. Esperar a Ollama
sleep 20

# 4. Descargar modelo
docker-compose exec ollama ollama pull gemma2

# 5. Ejecutar pipeline
docker-compose exec adk-pipeline python main.py
```

---

## Validación Post-Deployment

### 1. Verificar Servicios
```bash
# Todos deben estar "Up"
docker-compose ps

# Salida esperada:
# NAME                COMMAND             STATUS
# adk-ollama          ollama serve        Up
# adk-otel-collector  /otelcontribcol ... Up
# adk-prometheus      /bin/prometheus ... Up
# adk-grafana         /run.sh             Up
# adk-pipeline        python main.py      Up
```

### 2. Verificar Health Checks
```bash
# Ollama
curl http://localhost:11434/api/tags
# Respuesta: {"models": [{"name": "gemma2", ...}]}

# Prometheus
curl http://localhost:9090/-/healthy
# Respuesta: Prometheus is Healthy

# OTEL Collector
curl http://localhost:8888/metrics | head -20
# Respuesta: Métricas en formato Prometheus
```

### 3. Acceder a Dashboards
```bash
# Grafana
open http://localhost:3000
# Usuario: admin
# Contraseña: admin

# Prometheus
open http://localhost:9090

# Ollama API
open http://localhost:11434/api/tags
```

### 4. Verificar Archivos Generados
```bash
# Listar archivos en el contenedor
docker-compose exec adk-pipeline ls -la /app/work/poc-mongo-reactivo/

# Ver README generado
docker-compose exec adk-pipeline cat /app/work/poc-mongo-reactivo/README.md | head -50

# Ver CHANGELOG generado
docker-compose exec adk-pipeline cat /app/work/poc-mongo-reactivo/CHANGELOG.md
```

---

## Configuración en Producción

### Cambiar Repositorio
```bash
# Editar docker-compose.yml
environment:
  - GITHUB_REPO_SSH=git@github.com:otro-usuario/otro-repo.git

# O usar variable de entorno
export GITHUB_REPO_SSH="git@github.com:tu-repo/tu-proyecto.git"
docker-compose up adk-pipeline
```

### Cambiar Modelo Ollama
```bash
# Descargar modelo alternativo
./run.sh model qwen2.5-coder
# O
make model MODEL=mistral

# Cambiar en docker-compose.yml
environment:
  - MODEL_NAME=qwen2.5-coder
```

### Persistencia de Datos
```bash
# Volúmenes en docker-compose.yml:
volumes:
  ollama-data:        # Modelos Ollama descargados
  prometheus-data:    # Series temporales de Prometheus
  grafana-data:       # Configuración de Grafana
  adk-work:           # Repositorios clonados
```

### Logs Centralizados
```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs específicos
docker-compose logs -f adk-pipeline
docker-compose logs -f ollama
docker-compose logs -f otel-collector
```

---

## Troubleshooting Deployment

| Problema | Solución |
|----------|----------|
| Contenedor adk-pipeline no inicia | Verificar logs: `docker-compose logs adk-pipeline` |
| Ollama connection refused | Verificar puerto 11434: `lsof -i :11434` |
| SSH permission denied | Verificar permisos: `chmod 600 ~/.ssh/id_rsa` |
| Port already in use | Cambiar puerto en docker-compose.yml |
| Modelo no encontrado | Descargar: `./run.sh model gemma2` |
| Memory limit exceeded | Aumentar límite en docker-compose.yml |

---

## Monitoreo Continuo

### Métricas Importantes
```
Prometheus Queries:
- rate(otel_spans_total[5m])           # Tasa de spans
- histogram_quantile(0.95, ...)         # P95 latency
- rate(errors_total[5m])                # Tasa de errores
```

### Alertas Sugeridas
```yaml
- nombre: PipelineError
  condición: rate(errors_total[5m]) > 0.1
  
- nombre: HighLatency
  condición: histogram_quantile(0.95, latency) > 30s
  
- nombre: OllamaDown
  condición: up{job="ollama"} == 0
```

---

## Limpieza y Mantenimiento

### Limpiar Logs
```bash
# Borrar logs antiguos
docker-compose logs adk-pipeline | tail -100 > backup.log
docker-compose exec adk-pipeline rm -rf /app/logs/*
```

### Actualizar Modelos Ollama
```bash
# Listar modelos
docker-compose exec ollama ollama list

# Descargar nueva versión
docker-compose exec ollama ollama pull gemma2:latest
```

### Hacer Backup de Datos
```bash
# Backup de volúmenes
docker run --rm -v adk-prometheus-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/prometheus.tar.gz -C /data .

docker run --rm -v adk-grafana-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/grafana.tar.gz -C /data .
```

---

## Escalabilidad

### Multi-pipeline (Múltiples Repositorios)
```bash
# Crear otra instancia con diferente repo
docker-compose -f docker-compose.yml \
  -f docker-compose.additional.yml up -d

# En docker-compose.additional.yml:
services:
  adk-pipeline-2:
    build: .
    environment:
      GITHUB_REPO_SSH: git@github.com:otro/repo.git
```

### Cluster de Ollama
```bash
# Usar múltiples instancias de Ollama
# Considerar load balancing con nginx
```

---

## Deshabilitar Servicios (opcional)

```bash
# Solo ejecutar pipeline (sin observabilidad)
docker-compose up -d ollama adk-pipeline

# Solo Ollama + Pipeline (sin dashboards)
# Editar docker-compose.yml y comentar grafana, prometheus
```

---

## Validación Final

```bash
# Ejecutar checklist completo
./run.sh check          # Verificar prerequisites

docker-compose ps       # Todos Up
docker-compose logs -f  # Sin errores críticos

make info               # Ver configuración

# Test end-to-end
./run.sh run           # Debe completar exitosamente

# Verificar archivos generados
ls -la /tmp/adk-pipeline/poc-mongo-reactivo/
# README.md y CHANGELOG.md deben existir
```

✅ **Deployment completado exitosamente**

