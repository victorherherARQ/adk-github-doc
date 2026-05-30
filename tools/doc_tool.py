"""
Herramienta de Generación Automática de Documentación
Integrada con ADK 2.0 y Ollama
"""

import os
import json
import logging
import subprocess
from typing import Dict, Any
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

class DocumentationGeneratorTool:
    """Herramienta para generar README.md y CHANGELOG.md automáticamente"""
    
    def __init__(self, work_dir: str, ollama_endpoint: str, model: str = "gemma2"):
        self.work_dir = work_dir
        self.ollama_endpoint = ollama_endpoint
        self.model = model
        logger.info(f"DocumentationGeneratorTool inicializado con modelo: {model}")
    
    def generate_documentation(self, repo_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generar README.md y CHANGELOG.md para un repositorio.
        
        Args:
            repo_path: Ruta al repositorio clonado
            metadata: Metadatos del repositorio (opcional)
        
        Returns:
            Dict con rutas a archivos generados
        """
        try:
            logger.info(f"Generando documentación para: {repo_path}")
            
            # Extraer información del repositorio
            repo_info = self._analyze_repository(repo_path)
            
            # Generar README.md
            readme_path = os.path.join(repo_path, "README.md")
            readme_content = self._generate_readme(repo_info, metadata)
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logger.info(f"✓ README.md generado: {readme_path}")
            
            # Generar CHANGELOG.md
            changelog_path = os.path.join(repo_path, "CHANGELOG.md")
            changelog_content = self._generate_changelog(repo_path)
            
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(changelog_content)
            
            logger.info(f"✓ CHANGELOG.md generado: {changelog_path}")
            
            return {
                "status": "success",
                "readme_path": readme_path,
                "changelog_path": changelog_path,
                "repo_info": repo_info
            }
        
        except Exception as e:
            error_msg = f"Error al generar documentación: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analizar estructura y contenido del repositorio"""
        info = {
            "name": os.path.basename(repo_path),
            "description": "",
            "structure": [],
            "main_files": [],
            "has_tests": False,
            "has_docs": False,
            "languages": {}
        }
        
        try:
            # Analizar estructura
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
                level = root.replace(repo_path, '').count(os.sep)
                indent = ' ' * 2 * level
                rel_path = os.path.basename(root)
                
                if level < 3:  # Limitar profundidad
                    info["structure"].append(f"{indent}{rel_path}/")
                
                # Detectar directorios especiales
                if 'test' in root.lower() or 'spec' in root.lower():
                    info["has_tests"] = True
                if 'doc' in root.lower():
                    info["has_docs"] = True
            
            # Archivos principales
            for file in os.listdir(repo_path):
                if not file.startswith('.'):
                    info["main_files"].append(file)
            
            # Buscar description en package.json (si existe)
            package_json_path = os.path.join(repo_path, "package.json")
            if os.path.exists(package_json_path):
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    try:
                        pkg_data = json.load(f)
                        info["description"] = pkg_data.get("description", "")
                    except json.JSONDecodeError:
                        pass
            
            logger.info(f"Repositorio analizado: {info['name']}")
        
        except Exception as e:
            logger.warning(f"Error al analizar repositorio: {e}")
        
        return info
    
    def _generate_readme(self, repo_info: Dict[str, Any], metadata: Dict[str, Any] = None) -> str:
        """
        Generar contenido del README.md usando Ollama.
        
        Nota: Si Ollama no está disponible, genera un README estándar.
        """
        
        try:
            # Intentar usar Ollama para generar README mejorado
            prompt = f"""
Genera un README.md profesional para un repositorio con la siguiente información:

Nombre del proyecto: {repo_info.get('name', 'Proyecto')}
Descripción: {repo_info.get('description', 'Sin descripción')}
Archivos principales: {', '.join(repo_info.get('main_files', [])[:5])}
Tiene tests: {repo_info.get('has_tests', False)}
Tiene documentación: {repo_info.get('has_docs', False)}

El README debe incluir:
1. Título y descripción
2. Características principales
3. Requisitos de instalación
4. Guía de uso
5. Estructura del proyecto
6. Contribuciones
7. Licencia

Formato: Markdown puro, sin bloques de código adicionales.
"""
            
            readme = self._call_ollama(prompt)
            if readme:
                return readme
        
        except Exception as e:
            logger.warning(f"Error al usar Ollama: {e}. Generando README estándar...")
        
        # Generar README estándar si Ollama falla
        return self._generate_default_readme(repo_info)
    
    def _generate_default_readme(self, repo_info: Dict[str, Any]) -> str:
        """Generar README estándar (sin Ollama)"""
        
        name = repo_info.get('name', 'Proyecto')
        description = repo_info.get('description', '')
        has_tests = repo_info.get('has_tests', False)
        main_files = repo_info.get('main_files', [])
        
        readme = f"""# {name}

{description if description else 'Descripción del proyecto'}

## 📋 Características

- Característica 1
- Característica 2
- Característica 3

## 🚀 Inicio Rápido

### Requisitos

- Python 3.8+
- Git

### Instalación

```bash
git clone <repo-url>
cd {name}
pip install -r requirements.txt
```

## 📖 Uso

Ejemplo de uso básico:

```bash
python main.py
```

## 📁 Estructura del Proyecto

```
{name}/
├── README.md
├── requirements.txt
├── main.py
"""
        
        if main_files:
            readme += f"├── {main_files[0]}\n"
        
        readme += """└── ...
```

## 🧪 Tests

"""
        
        if has_tests:
            readme += "```bash\npytest\n```\n"
        else:
            readme += "No hay tests configurados.\n"
        
        readme += """
## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo licencia MIT.

---

*Generado automáticamente por ADK 2.0*
"""
        
        return readme
    
    def _generate_changelog(self, repo_path: str) -> str:
        """
        Generar CHANGELOG.md basado en los commits del repositorio.
        """
        
        changelog = """# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/es/).

## [Unreleased]

### Added
- Funcionalidad inicial generada automáticamente

### Changed
- Cambios iniciales

### Fixed
- Correcciones iniciales

---

## Versiones Anteriores

Este proyecto fue generado automáticamente usando **ADK 2.0**.

Para ver el historial completo de cambios, consulta los commits en GitHub.

*Última actualización: Generada automáticamente por ADK 2.0*
"""
        
        try:
            # Intentar extraer información de commits
            result = subprocess.run(
                ['git', 'log', '--oneline', '-20'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                commits = result.stdout.strip().split('\n')
                
                changelog = """# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

"""
                changelog += "## Commits Recientes\n\n"
                
                for commit in commits[:10]:
                    changelog += f"- {commit}\n"
                
                changelog += "\n*Generado automáticamente por ADK 2.0*\n"
        
        except Exception as e:
            logger.warning(f"Error al extraer commits: {e}")
        
        return changelog
    
    def _call_ollama(self, prompt: str, max_retries: int = 3) -> str:
        """
        Llamar a Ollama para generar contenido usando LLM.
        
        Args:
            prompt: El prompt para el modelo
            max_retries: Número máximo de reintentos
        
        Returns:
            Texto generado por el modelo, o None si falla
        """
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.ollama_endpoint}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.7,
                        "num_predict": 1024
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', '')
                else:
                    logger.warning(f"Ollama respondió con código: {response.status_code}")
            
            except requests.Timeout:
                logger.warning(f"Timeout en Ollama (intento {attempt + 1}/{max_retries})")
            except Exception as e:
                logger.warning(f"Error al llamar Ollama: {e}")
            
            if attempt < max_retries - 1:
                import time
                time.sleep(2)
        
        return None
    
    def validate_markdown(self, file_path: str) -> Dict[str, Any]:
        """Validar que un archivo Markdown sea válido"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validaciones básicas
            return {
                "is_valid": True,
                "size": len(content),
                "has_headings": '#' in content,
                "has_links": '[' in content and ']' in content
            }
        except Exception as e:
            logger.error(f"Error al validar markdown: {e}")
            return {"is_valid": False, "error": str(e)}
