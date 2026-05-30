#!/usr/bin/env python3
"""
Pipeline de Generación Automática de README.md y CHANGELOG.md
Utilizando Google ADK 2.0 con Workflow DAG y OpenTelemetry
"""

import os
import sys
import logging
from typing import Any

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Google ADK imports
try:
    from google.adk import Agent, Workflow, Task
    from google.adk.runtime import run
except ImportError:
    print("Error: google-adk no está instalado. Ejecuta: pip install google-adk")
    sys.exit(1)

# Importar herramientas personalizadas
from tools.github_tool import GitHubCloneTool
from tools.doc_tool import DocumentationGeneratorTool

# ==================== CONFIGURACIÓN ====================

# Variables de entorno
GITHUB_REPO_SSH = os.getenv("GITHUB_REPO_SSH", "git@github.com:victorherherARQ/poc-mongo-reactivo.git")
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
OTEL_ENDPOINT = os.getenv("OTEL_ENDPOINT", "http://localhost:4317")
WORK_DIR = os.getenv("WORK_DIR", "/tmp/adk-pipeline")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma2")  # o "qwen2.5-coder"

# Crear directorio de trabajo si no existe
os.makedirs(WORK_DIR, exist_ok=True)

# ==================== CONFIGURACIÓN DE LOGGING ====================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURACIÓN DE OPENTELEMETRY ====================

def init_otel():
    """Inicializar OpenTelemetry con exportador OTLP"""
    try:
        # Trace Provider
        otlp_exporter = OTLPSpanExporter(endpoint=OTEL_ENDPOINT)
        trace_provider = TracerProvider()
        trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        trace.set_tracer_provider(trace_provider)
        
        # Metric Provider
        metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=OTEL_ENDPOINT))
        meter_provider = MeterProvider(metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)
        
        # Instrumentación automática
        RequestsInstrumentor().instrument()
        
        logger.info(f"✓ OpenTelemetry inicializado. Endpoint: {OTEL_ENDPOINT}")
        return trace.get_tracer(__name__)
    except Exception as e:
        logger.warning(f"⚠ No se pudo conectar a OpenTelemetry: {e}")
        return trace.get_tracer(__name__)

tracer = init_otel()

# ==================== DEFINICIÓN DE AGENTES ESPECIALIZADOS ====================

# Instanciar herramientas
github_tool = GitHubCloneTool(work_dir=WORK_DIR)
doc_tool = DocumentationGeneratorTool(
    work_dir=WORK_DIR,
    ollama_endpoint=OLLAMA_ENDPOINT,
    model=MODEL_NAME
)

# Crear Agente de Git
git_agent = Agent(
    name="git_clone_agent",
    instructions="""
    Eres un agente especializado en clonación de repositorios Git por SSH.
    
    Tu tarea:
    1. Clonar el repositorio desde: {repo_ssh}
    2. Validar la estructura del directorio clonado
    3. Extraer metadatos del repositorio (autor, descripción, licencia)
    4. Pasar la ruta clonada al siguiente agente
    
    Utiliza la herramienta 'clone_repository' para realizar el clonado.
    """.format(repo_ssh=GITHUB_REPO_SSH),
    tools=[github_tool],
    model=f"ollama://{MODEL_NAME}",
    api_endpoint=OLLAMA_ENDPOINT
)

# Crear Agente de Documentación
doc_agent = Agent(
    name="doc_generation_agent",
    instructions="""
    Eres un agente especializado en generación automática de documentación en Markdown.
    
    Tu tarea:
    1. Analizar la estructura del repositorio proporcionado
    2. Generar README.md optimizado con:
       - Descripción del proyecto
       - Requisitos de instalación
       - Guía de uso
       - Contribuciones esperadas
    3. Generar CHANGELOG.md basado en commits
    4. Validar que ambos archivos sean sintácticamente correctos
    
    Utiliza la herramienta 'generate_documentation' para crear los archivos.
    """,
    tools=[doc_tool],
    model=f"ollama://{MODEL_NAME}",
    api_endpoint=OLLAMA_ENDPOINT
)

# ==================== DEFINICIÓN DEL WORKFLOW ====================

def create_pipeline_workflow():
    """
    Crear el Workflow DAG para el pipeline de documentación.
    
    Estructura:
        START -> git_agent -> doc_agent -> END
    """
    
    workflow = Workflow(
        name="github_doc_pipeline",
        description="Pipeline de generación automática de documentación GitHub con ADK 2.0",
        agents=[git_agent, doc_agent],
        edges=[
            # (source_agent, target_agent)
            ("START", git_agent.name),
            (git_agent.name, doc_agent.name),
            (doc_agent.name, "END")
        ]
    )
    
    logger.info("✓ Workflow DAG creado exitosamente")
    return workflow

# ==================== EJECUTOR DEL PIPELINE ====================

def main():
    """Función principal para ejecutar el pipeline"""
    
    logger.info("=" * 60)
    logger.info("INICIANDO PIPELINE ADK 2.0 - GENERACIÓN DE DOCUMENTACIÓN")
    logger.info("=" * 60)
    logger.info(f"📍 Repositorio: {GITHUB_REPO_SSH}")
    logger.info(f"🤖 Modelo: {MODEL_NAME}")
    logger.info(f"📊 OpenTelemetry: {OTEL_ENDPOINT}")
    logger.info(f"💾 Directorio de trabajo: {WORK_DIR}")
    logger.info("=" * 60)
    
    with tracer.start_as_current_span("pipeline_execution"):
        try:
            # Crear el workflow
            pipeline = create_pipeline_workflow()
            
            # Ejecutar el workflow
            logger.info("▶ Ejecutando workflow...")
            result = run(
                workflow=pipeline,
                initial_input={
                    "repo_ssh": GITHUB_REPO_SSH,
                    "work_dir": WORK_DIR
                },
                max_iterations=10
            )
            
            logger.info("✓ Pipeline ejecutado exitosamente")
            logger.info(f"📋 Resultado: {result}")
            
            # Log final
            logger.info("=" * 60)
            logger.info("✓ DOCUMENTACIÓN GENERADA")
            logger.info(f"📁 Ubicación: {WORK_DIR}")
            logger.info("=" * 60)
            
            return result
            
        except Exception as e:
            logger.error(f"✗ Error en pipeline: {e}", exc_info=True)
            with tracer.start_as_current_span("error_handler"):
                tracer.get_current_span().set_attribute("error", str(e))
            sys.exit(1)

if __name__ == "__main__":
    main()
