.PHONY: help setup build start stop run logs status grafana model cleanup

# Variables
DOCKER_COMPOSE := docker-compose -f docker-compose.yml
MODEL ?= gemma2
REPO ?= git@github.com:victorherherARQ/poc-mongo-reactivo.git

# Default target
help:
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║          ADK 2.0 - Pipeline de Documentación GitHub           ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Comandos disponibles:"
	@echo ""
	@echo "  make help          - Mostrar esta ayuda"
	@echo "  make setup         - Setup inicial (build + start + modelo)"
	@echo "  make build         - Construir imágenes Docker"
	@echo "  make start         - Iniciar servicios"
	@echo "  make stop          - Detener servicios"
	@echo "  make run           - Ejecutar pipeline"
	@echo "  make logs          - Ver logs en vivo"
	@echo "  make status        - Ver estado de servicios"
	@echo "  make grafana       - Abrir dashboard Grafana"
	@echo "  make model MODEL=qwen2.5-coder  - Descargar modelo"
	@echo "  make cleanup       - Limpiar y eliminar volúmenes"
	@echo ""
	@echo "Ejemplos:"
	@echo "  make setup                              # Setup inicial"
	@echo "  make run                                # Ejecutar pipeline"
	@echo "  make model MODEL=mistral                # Descargar modelo alternativo"
	@echo ""

# Setup inicial
setup: build start model
	@echo "✓ Setup completado. Ejecuta: make run"

# Build
build:
	@echo "🔨 Construyendo imágenes Docker..."
	@$(DOCKER_COMPOSE) build
	@echo "✓ Build completado"

# Start
start:
	@echo "▶️  Iniciando servicios..."
	@$(DOCKER_COMPOSE) up -d
	@echo "⏳ Esperando servicios..."
	@sleep 10
	@echo "✓ Servicios iniciados"
	@echo ""
	@echo "📊 Dashboards:"
	@echo "  - Grafana:   http://localhost:3000"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Ollama:    http://localhost:11434"

# Stop
stop:
	@echo "⏹️  Deteniendo servicios..."
	@$(DOCKER_COMPOSE) down
	@echo "✓ Servicios detenidos"

# Run pipeline
run:
	@echo "▶️  Ejecutando pipeline ADK 2.0..."
	@$(DOCKER_COMPOSE) exec adk-pipeline python main.py

# Logs
logs:
	@$(DOCKER_COMPOSE) logs -f adk-pipeline

# Status
status:
	@$(DOCKER_COMPOSE) ps

# Grafana
grafana:
	@echo "📊 Abriendo Grafana..."
	@command -v xdg-open > /dev/null && xdg-open http://localhost:3000 || \
	command -v open > /dev/null && open http://localhost:3000 || \
	echo "Por favor abre: http://localhost:3000"

# Descargar modelo
model:
	@echo "📥 Descargando modelo: $(MODEL)..."
	@$(DOCKER_COMPOSE) exec ollama ollama pull $(MODEL)
	@echo "✓ Modelo descargado"

# Cleanup
cleanup:
	@echo "🧹 Limpiando..."
	@$(DOCKER_COMPOSE) down -v
	@echo "✓ Limpieza completada"

# Ver estructura del proyecto
tree:
	@tree -I '.git|__pycache__|*.pyc' -L 2 .

# Verificar prerequisites
check:
	@echo "Verificando prerequisites..."
	@command -v docker > /dev/null && echo "✓ Docker" || echo "✗ Docker no encontrado"
	@command -v docker-compose > /dev/null && echo "✓ Docker Compose" || echo "✗ Docker Compose no encontrado"
	@command -v git > /dev/null && echo "✓ Git" || echo "✗ Git no encontrado"
	@test -f ~/.ssh/id_rsa && echo "✓ SSH key" || echo "⚠ SSH key no encontrada (~/ssh/id_rsa)"
	@ssh -T git@github.com > /dev/null 2>&1 && echo "✓ GitHub SSH" || echo "⚠ GitHub SSH no configurado"

# Limpiar logs
clean-logs:
	@rm -rf ./logs/*
	@echo "✓ Logs limpiados"

# Ver información del sistema
info:
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║                    INFORMACIÓN DEL SISTEMA                    ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🔧 Configuración:"
	@echo "  Modelo: $(MODEL)"
	@echo "  Repositorio: $(REPO)"
	@echo ""
	@echo "📁 Directorios:"
	@echo "  Trabajo: /app/work (dentro del contenedor)"
	@echo "  Logs: ./logs"
	@echo ""
	@echo "🌐 Endpoints:"
	@echo "  Grafana:     http://localhost:3000 (admin/admin)"
	@echo "  Prometheus:  http://localhost:9090"
	@echo "  Ollama:      http://localhost:11434"
	@echo "  OTLP gRPC:   http://localhost:4317"
	@echo "  OTLP HTTP:   http://localhost:4318"
