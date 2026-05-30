# 🏗️ ARQUITECTURA ADK 2.0 - Pipeline de Documentación

## Visión General

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE ADK 2.0                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    WORKFLOW DAG                          │  │
│  │  START → git_clone_agent → doc_generation_agent → END   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────────────┐     │
│  │  git_clone_agent │         │ doc_generation_agent     │     │
│  │                  │         │                          │     │
│  │ Tools:           │         │ Tools:                   │     │
│  │ - GitHubClone    │◄───────►│ - DocGenerator           │     │
│  │                  │         │                          │     │
│  │ Output:          │         │ Output:                  │     │
│  │ - repo_path      │         │ - readme_path            │     │
│  │ - metadata       │         │ - changelog_path         │     │
│  └──────────────────┘         └──────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

                            ▼

┌─────────────────────────────────────────────────────────────────┐
│              INFRAESTRUCTURA DOCKER COMPOSE                      │
│                                                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │   Ollama        │  │ OTEL Collector   │  │  Prometheus    │ │
│  │ :11434          │  │ :4317 / :4318    │  │   :9090        │ │
│  └─────────────────┘  └──────────────────┘  └────────────────┘ │
│                                                                 │
│  ┌──────────────────┐  ┌─────────────────────────────────────┐ │
│  │   Grafana        │  │   ADK Pipeline                      │ │
│  │  :3000           │  │   - main.py                         │ │
│  │ (admin/admin)    │  │   - Workflow Executor               │ │
│  └──────────────────┘  │   - OpenTelemetry Instrumented      │ │
│                        │   - SSH Integration                 │ │
│                        └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Componentes Principales

### 1. **Workflow DAG (main.py)**

```python
workflow = Workflow(
    name="github_doc_pipeline",
    edges=[
        ("START", "git_clone_agent"),
        ("git_clone_agent", "doc_generation_agent"),
        ("doc_generation_agent", "END")
    ]
)
```

**Características:**
- Grafo determinista (DAG)
- Ejecución secuencial
- Passthrough de datos entre agentes
- Error handling integrado

---

### 2. **Agentes ADK 2.0**

#### **git_clone_agent**
```python
git_agent = Agent(
    name="git_clone_agent",
    instructions="Clonar repo SSH...",
    tools=[github_tool],
    model="ollama://gemma2",
    api_endpoint="http://ollama:11434"
)
```

**Flujo:**
1. Recibe URL SSH del repositorio
2. Valida conectividad SSH
3. Clona el repositorio
4. Extrae metadatos
5. Pasa ruta al siguiente agente

#### **doc_generation_agent**
```python
doc_agent = Agent(
    name="doc_generation_agent",
    instructions="Generar docs...",
    tools=[doc_tool],
    model="ollama://gemma2",
    api_endpoint="http://ollama:11434"
)
```

**Flujo:**
1. Recibe ruta del repositorio
2. Analiza estructura del código
3. Genera README.md (con ayuda de Ollama)
4. Genera CHANGELOG.md
5. Valida archivos Markdown

---

### 3. **Herramientas (Tools)**

#### **GitHubCloneTool**
```python
class GitHubCloneTool:
    def clone_repository(repo_ssh) → Dict
    def _extract_metadata(repo_path) → Dict
    def _detect_languages(repo_path) → Dict
    def validate_repository(repo_path) → Dict
```

**Métodos:**
- `clone_repository()` - Clonado SSH
- `_extract_metadata()` - Extrae info del repo
- `_detect_languages()` - Detecta lenguajes
- `validate_repository()` - Valida integridad

#### **DocumentationGeneratorTool**
```python
class DocumentationGeneratorTool:
    def generate_documentation(repo_path) → Dict
    def _analyze_repository(repo_path) → Dict
    def _generate_readme(repo_info) → str
    def _generate_changelog(repo_path) → str
    def _call_ollama(prompt) → str
    def validate_markdown(file_path) → Dict
```

**Métodos:**
- `generate_documentation()` - Genera docs
- `_analyze_repository()` - Analiza código
- `_generate_readme()` - README mejorado con LLM
- `_generate_changelog()` - Historial de commits
- `_call_ollama()` - Integración con LLM
- `validate_markdown()` - Valida sintaxis

---

### 4. **Observabilidad OpenTelemetry**

```
┌──────────────────────────────────────────────┐
│           ADK Pipeline                       │
│  (Traces & Metrics Instrumented)             │
└────────────────┬─────────────────────────────┘
                 │
         ┌───────▼───────┐
         │ OTLP Exporter │
         │ :4317 (gRPC)  │
         └───────┬───────┘
                 │
         ┌───────▼──────────────┐
         │ OTEL Collector       │
         │ - Memory Limiter     │
         │ - Batch Processor    │
         └───────┬──────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼──────┐          ┌──────▼────┐
│Prometheus│          │Logging    │
│ Exporter │          │Exporter   │
└───┬──────┘          └───────────┘
    │
    └─────────────────────┐
                    ┌─────▼─────┐
                    │ Grafana   │
                    │ Dashboard │
                    └───────────┘
```

**Instrumentación:**
- Span collection en cada paso del workflow
- Métricas de ejecución (latencia, errores)
- Traces distribuidos
- Exportación OTLP a OpenTelemetry Collector

---

### 5. **Docker Compose Orchestration**

```yaml
services:
  ollama:
    - LLM local
    - Volumen persistente
    - Health check
  
  otel-collector:
    - Recolecta traces y métricas
    - Procesa datos
    - Exporta a Prometheus
  
  prometheus:
    - Scrapes OTEL metrics
    - Time-series database
    - Datasource de Grafana
  
  grafana:
    - Dashboard visual
    - Alertas configurables
  
  adk-pipeline:
    - Contenedor principal
    - SSH mounted volume
    - Network internal
```

---

## 📊 Flujo de Datos

### Input
```json
{
  "repo_ssh": "git@github.com:victorherherARQ/poc-mongo-reactivo.git",
  "work_dir": "/app/work"
}
```

### Transformación (git_clone_agent)
```json
{
  "repo_path": "/app/work/poc-mongo-reactivo",
  "metadata": {
    "has_tests": true,
    "has_docs": true,
    "languages": {
      "TypeScript": 42,
      "JavaScript": 15,
      "JSON": 8
    }
  }
}
```

### Transformación (doc_generation_agent)
```json
{
  "readme_path": "/app/work/poc-mongo-reactivo/README.md",
  "changelog_path": "/app/work/poc-mongo-reactivo/CHANGELOG.md",
  "validation": {
    "readme_valid": true,
    "changelog_valid": true
  }
}
```

---

## 🔄 Ciclo de Vida de Ejecución

```
START
  │
  ├─ Initialize OpenTelemetry
  │   └─ Create Tracer Provider
  │
  ├─ Load Environment Variables
  │   └─ GITHUB_REPO_SSH, OLLAMA_ENDPOINT, OTEL_ENDPOINT
  │
  ├─ Create Agents
  │   ├─ git_clone_agent (with tools)
  │   └─ doc_generation_agent (with tools)
  │
  ├─ Build Workflow DAG
  │   └─ Define edges and transitions
  │
  ├─► EXECUTE WORKFLOW
  │   │
  │   ├─ git_clone_agent
  │   │   ├─ Start Span: "git_clone"
  │   │   ├─ Execute: GitHubCloneTool.clone_repository()
  │   │   ├─ Extract metadata
  │   │   └─ End Span
  │   │
  │   └─ doc_generation_agent
  │       ├─ Start Span: "doc_generation"
  │       ├─ Analyze repository
  │       ├─ Call Ollama for README content
  │       ├─ Generate CHANGELOG from commits
  │       ├─ Validate Markdown
  │       └─ End Span
  │
  ├─ Export Spans to OTLP
  │
  └─ END
     └─ Return results
```

---

## 🛡️ Error Handling

```
try:
  Execute workflow
  
  ├─ git_clone_agent
  │   ├─ SSH connection error
  │   │   └─ Retry with backoff
  │   ├─ Repository not found
  │   │   └─ Log error, continue
  │   └─ Clone timeout
  │       └─ Fail gracefully
  │
  └─ doc_generation_agent
      ├─ Ollama unavailable
      │   └─ Fall back to default templates
      ├─ File write error
      │   └─ Retry with different path
      └─ Invalid Markdown syntax
          └─ Log warning, continue

finally:
  Export traces
  Close connections
  Log summary
```

---

## 📈 Métricas Disponibles

### Application Metrics
- `pipeline_execution_duration` - Tiempo total
- `git_clone_duration` - Tiempo de clonado
- `doc_generation_duration` - Tiempo de generación
- `ollama_inference_duration` - Latencia de LLM
- `error_count` - Contador de errores

### System Metrics
- `otel_process_cpu_time` - CPU usado
- `otel_process_memory_usage` - Memoria usada
- `otel_process_runtime_go_goroutines` - Goroutines activas

---

## 🔐 Security Considerations

1. **SSH Integration**
   - Clave SSH mounted como read-only
   - No se almacena en el contenedor
   - Permisos 0600 validados

2. **OpenTelemetry**
   - No transmite datos sensibles
   - Traces sanitizados
   - OTLP sin autenticación (local network)

3. **Ollama Local**
   - No envía datos a internet
   - Completamente local
   - API sin autenticación (network internal)

4. **Docker**
   - Contenedores aislados
   - Red interna (bridge)
   - Volúmenes con restricciones

---

## 📦 Requisitos

| Componente | Versión | Función |
|-----------|---------|---------|
| Python | 3.11+ | Runtime |
| Docker | 20.10+ | Containerización |
| Docker Compose | 2.0+ | Orquestación |
| Google ADK | 2.0+ | Framework |
| Ollama | Latest | LLM Local |
| OpenTelemetry | 1.21+ | Observabilidad |

---

## 🚀 Próximas Mejoras

- [ ] Soporte para múltiples repositorios simultáneamente
- [ ] Cache de modelos Ollama
- [ ] Alertas automáticas en Grafana
- [ ] Integración con webhooks GitHub
- [ ] Versionamiento de documentación generada
- [ ] Machine Learning para mejora de templates
- [ ] API REST para ejecutar pipeline remotamente

---

*Documentación actualizada: Mayo 2026*
