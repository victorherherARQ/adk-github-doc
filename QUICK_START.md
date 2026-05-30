# 🚀 QUICK START - ADK 2.0 Pipeline

## En 3 pasos

### ✅ Paso 1: Verificar Prerequisites
```bash
docker --version        # Docker 20.10+
docker-compose --version  # Docker Compose 2.0+
ssh -T git@github.com   # SSH configurado
```

### ✅ Paso 2: Setup Inicial (automático)
```bash
cd adk-github-doc
chmod +x run.sh
./run.sh setup

# Esto hará:
# 1. Build de imágenes Docker
# 2. Inicia todos los servicios (Ollama, Prometheus, Grafana)
# 3. Descarga modelo LLM (gemma2)
# 4. Espera a que Ollama esté listo
```

### ✅ Paso 3: Ejecutar Pipeline
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

---

## 📊 Dashboards

- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **Ollama:** http://localhost:11434

---

## 📝 Archivos Generados

Los archivos README.md y CHANGELOG.md se crearán en:
```
/tmp/adk-pipeline/poc-mongo-reactivo/
├── README.md       ✓ Generado automáticamente
├── CHANGELOG.md    ✓ Generado automáticamente
└── ...otros archivos del repo
```

Copiar archivos generados:
```bash
docker-compose exec adk-pipeline cat /app/work/poc-mongo-reactivo/README.md
docker-compose exec adk-pipeline cat /app/work/poc-mongo-reactivo/CHANGELOG.md
```

---

## 🔧 Comandos Útiles

```bash
./run.sh run              # Ejecutar pipeline
./run.sh logs             # Ver logs en vivo
./run.sh status           # Ver estado de servicios
./run.sh grafana          # Abrir Grafana
./run.sh stop             # Detener servicios
./run.sh model qwen2.5-coder  # Cambiar modelo LLM
./run.sh cleanup          # Limpiar todo
```

---

## ⚠️ Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| SSH key not found | `ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa` |
| Ollama connection refused | `./run.sh status` → verificar ollama RUNNING |
| Port 11434 in use | `lsof -i :11434` → `kill -9 <PID>` |
| Modelo no disponible | `./run.sh model gemma2` |

---

**¡Listo! El pipeline está configurado y ejecutándose.**
