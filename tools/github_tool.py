"""
Herramienta de Clonación de Repositorios GitHub por SSH
Integrada con ADK 2.0
"""

import os
import subprocess
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class GitHubCloneTool:
    """Herramienta para clonar repositorios Git usando SSH"""
    
    def __init__(self, work_dir: str = "/tmp/adk-pipeline"):
        self.work_dir = work_dir
        os.makedirs(self.work_dir, exist_ok=True)
        logger.info(f"GitHubCloneTool inicializado en: {self.work_dir}")
    
    def clone_repository(self, repo_ssh: str) -> Dict[str, Any]:
        """
        Clonar un repositorio usando SSH.
        
        Args:
            repo_ssh: URL SSH del repositorio (ej: git@github.com:user/repo.git)
        
        Returns:
            Dict con información del clonado
        """
        try:
            # Extraer nombre del repositorio
            repo_name = repo_ssh.split('/')[-1].replace('.git', '')
            repo_path = os.path.join(self.work_dir, repo_name)
            
            # Si ya existe, eliminar
            if os.path.exists(repo_path):
                logger.info(f"Eliminando repositorio existente: {repo_path}")
                subprocess.run(['rm', '-rf', repo_path], check=True)
            
            # Clonar el repositorio
            logger.info(f"Clonando repositorio: {repo_ssh}")
            subprocess.run(
                ['git', 'clone', repo_ssh, repo_path],
                check=True,
                capture_output=True,
                timeout=60
            )
            
            logger.info(f"✓ Repositorio clonado en: {repo_path}")
            
            # Extraer metadatos
            metadata = self._extract_metadata(repo_path)
            
            return {
                "status": "success",
                "repo_name": repo_name,
                "repo_path": repo_path,
                "metadata": metadata
            }
        
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout al clonar: {repo_ssh}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        except subprocess.CalledProcessError as e:
            error_msg = f"Error en clonado: {e.stderr.decode() if e.stderr else str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _extract_metadata(self, repo_path: str) -> Dict[str, Any]:
        """Extraer metadatos del repositorio"""
        metadata = {
            "files": [],
            "languages": {},
            "has_readme": False,
            "has_changelog": False,
            "has_license": False
        }
        
        try:
            # Listar archivos principales
            for item in os.listdir(repo_path):
                if not item.startswith('.'):
                    metadata["files"].append(item)
                    
                    # Detectar archivos especiales
                    if item.upper() == "README.MD":
                        metadata["has_readme"] = True
                    elif item.upper() == "CHANGELOG.MD":
                        metadata["has_changelog"] = True
                    elif item.upper() == "LICENSE":
                        metadata["has_license"] = True
            
            # Detectar lenguajes de programación
            metadata["languages"] = self._detect_languages(repo_path)
            
            logger.info(f"Metadatos extraídos: {metadata}")
            
        except Exception as e:
            logger.warning(f"Error al extraer metadatos: {e}")
        
        return metadata
    
    def _detect_languages(self, repo_path: str) -> Dict[str, int]:
        """Detectar lenguajes de programación en el repositorio"""
        languages = {}
        extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.jsx': 'React',
            '.tsx': 'React TS',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.sql': 'SQL',
            '.sh': 'Shell'
        }
        
        try:
            for root, dirs, files in os.walk(repo_path):
                # Ignorar directorios comunes
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv']]
                
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in extensions:
                        lang = extensions[ext]
                        languages[lang] = languages.get(lang, 0) + 1
        
        except Exception as e:
            logger.warning(f"Error al detectar lenguajes: {e}")
        
        return languages
    
    def validate_repository(self, repo_path: str) -> Dict[str, Any]:
        """Validar que el repositorio está correctamente clonado"""
        return {
            "is_valid": os.path.isdir(repo_path),
            "has_git_dir": os.path.isdir(os.path.join(repo_path, '.git')),
            "path": repo_path
        }
