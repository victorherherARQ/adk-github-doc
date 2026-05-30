#!/bin/bash

# Script de ayuda para ejecutar el pipeline ADK 2.0

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones
print_header() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Verificar Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        exit 1
    fi
    print_success "Docker encontrado"
}

# Verificar Docker Compose
check_docker_compose() {
    if ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose no está instalado"
        exit 1
    fi
    print_success "Docker Compose encontrado"
}

# Crear directorio logs
create_logs_dir() {
    mkdir -p "$SCRIPT_DIR/logs"
    print_success "Directorio de logs creado"
}

# Build de servicios
build_services() {
    print_header "Construyendo servicios Docker..."
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" build
    print_success "Servicios construidos"
}

# Iniciar servicios
start_services() {
    print_header "Iniciando servicios..."
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" up -d
    print_success "Servicios iniciados"
    
    sleep 15
    
    print_info "Esperando a que Ollama esté disponible..."
    for i in {1..60}; do
        if nc -z localhost 11434 2>/dev/null; then
            print_success "Ollama está disponible"
            sleep 5  # Extra wait for Ollama to fully initialize
            break
        fi
        if [ $i -eq 60 ]; then
            print_error "Timeout esperando a Ollama"
            print_error "Verifica los logs: docker compose logs ollama"
            exit 1
        fi
        echo -n "."
        sleep 1
    done
}

# Descargar modelo Ollama
download_ollama_model() {
    MODEL=${1:-gemma2}
    print_info "Descargando modelo Ollama: $MODEL"
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" exec -T ollama ollama pull "$MODEL"
    print_success "Modelo descargado"
}

# Ejecutar pipeline
run_pipeline() {
    print_header "Ejecutando pipeline ADK 2.0..."
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" exec adk-pipeline python main.py
}

# Ver logs
view_logs() {
    print_header "Logs del Pipeline"
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" logs -f adk-pipeline
}

# Ver dashboard Grafana
open_grafana() {
    print_info "Abriendo Grafana en http://localhost:3000"
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000
    elif command -v open &> /dev/null; then
        open http://localhost:3000
    else
        print_info "Por favor abre manualmente: http://localhost:3000"
    fi
}

# Limpiar servicios
cleanup() {
    print_header "Deteniendo servicios..."
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" down
    print_success "Servicios detenidos"
}

# Mostrar status
show_status() {
    print_header "Status de Servicios"
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" ps
}

# Main
main() {
    case "${1:-help}" in
        "help")
            echo "Uso: $0 [comando]"
            echo ""
            echo "Comandos disponibles:"
            echo "  help              - Mostrar esta ayuda"
            echo "  setup             - Configurar ambiente (build + start + descargar modelo)"
            echo "  build             - Construir imágenes Docker"
            echo "  start             - Iniciar servicios"
            echo "  stop              - Detener servicios"
            echo "  run               - Ejecutar pipeline"
            echo "  logs              - Ver logs del pipeline"
            echo "  status            - Ver estado de servicios"
            echo "  grafana           - Abrir dashboard Grafana"
            echo "  cleanup           - Limpiar y detener todo"
            echo "  model [nombre]    - Descargar modelo Ollama (defecto: gemma2)"
            echo ""
            echo "Ejemplos:"
            echo "  $0 setup                 # Configuración inicial"
            echo "  $0 run                   # Ejecutar pipeline"
            echo "  $0 model qwen2.5-coder   # Descargar modelo alternativo"
            ;;
        "setup")
            check_docker
            check_docker_compose
            create_logs_dir
            build_services
            start_services
            download_ollama_model ${2:-gemma2}
            print_header "¡Setup completado!"
            print_info "Ejecuta: $0 run"
            ;;
        "build")
            check_docker
            check_docker_compose
            build_services
            ;;
        "start")
            check_docker
            check_docker_compose
            create_logs_dir
            start_services
            ;;
        "stop")
            cleanup
            ;;
        "run")
            check_docker
            check_docker_compose
            run_pipeline
            ;;
        "logs")
            check_docker
            check_docker_compose
            view_logs
            ;;
        "status")
            check_docker
            check_docker_compose
            show_status
            ;;
        "grafana")
            open_grafana
            ;;
        "cleanup")
            cleanup
            ;;
        "model")
            check_docker
            check_docker_compose
            download_ollama_model ${2:-gemma2}
            ;;
        *)
            print_error "Comando desconocido: $1"
            echo ""
            $0 help
            exit 1
            ;;
    esac
}

main "$@"
