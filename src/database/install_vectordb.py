#!/usr/bin/env python3
"""
Script de Instalación Automatizada para Base de Datos Vectorial

Este script automatiza la instalación y configuración inicial de la base de datos
vectorial con Pinecone para documentos legales mexicanos.

Ejemplos de uso:
    python install_vectordb.py --setup-env
    python install_vectordb.py --install-deps
    python install_vectordb.py --test-connection
    python install_vectordb.py --full-setup

Autor: Asistente IA
Fecha: 2024
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VectorDBInstaller:
    """
    Instalador automatizado para la base de datos vectorial
    """
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.requirements_file = self.project_root / "requirements_vectordb.txt"
        self.config_example = self.project_root / "config_vectordb.env.example"
        self.config_file = self.project_root / "config_vectordb.env"
        
    def check_python_version(self) -> bool:
        """
        Verifica que la versión de Python sea compatible
        
        Returns:
            bool: True si la versión es compatible
        """
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            logger.error(f"Python {version.major}.{version.minor} no es compatible")
            logger.error("Se requiere Python 3.8 o superior")
            return False
        
        logger.info(f"Python {version.major}.{version.minor}.{version.micro} ✓")
        return True
    
    def install_dependencies(self) -> bool:
        """
        Instala las dependencias necesarias
        
        Returns:
            bool: True si la instalación fue exitosa
        """
        try:
            if not self.requirements_file.exists():
                logger.error(f"Archivo {self.requirements_file} no encontrado")
                return False
            
            logger.info("Instalando dependencias...")
            
            # Actualizar pip primero
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            # Instalar dependencias
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)
            ], check=True, capture_output=True, text=True)
            
            logger.info("Dependencias instaladas correctamente ✓")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error instalando dependencias: {e}")
            if e.stdout:
                logger.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                logger.error(f"STDERR: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return False
    
    def setup_environment_file(self) -> bool:
        """
        Configura el archivo de variables de entorno
        
        Returns:
            bool: True si la configuración fue exitosa
        """
        try:
            if self.config_file.exists():
                logger.info(f"Archivo {self.config_file.name} ya existe")
                response = input("¿Deseas sobrescribirlo? (y/N): ").strip().lower()
                if response != 'y':
                    logger.info("Configuración de entorno omitida")
                    return True
            
            if not self.config_example.exists():
                logger.error(f"Archivo {self.config_example} no encontrado")
                return False
            
            # Copiar archivo de ejemplo
            with open(self.config_example, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Solicitar configuración interactiva
            print("\n" + "="*60)
            print("CONFIGURACIÓN DE VARIABLES DE ENTORNO")
            print("="*60)
            
            # Pinecone API Key
            print("\n1. PINECONE API KEY")
            print("   Obtén tu API key gratuita en: https://app.pinecone.io/")
            pinecone_key = input("   Ingresa tu Pinecone API Key: ").strip()
            
            if pinecone_key:
                content = content.replace("your_pinecone_api_key_here", pinecone_key)
            
            # Modelo de embeddings
            print("\n2. MODELO DE EMBEDDINGS")
            print("   Opciones disponibles:")
            print("   1. sentence-transformers/all-MiniLM-L6-v2 (gratuito, rápido, 384 dim)")
            print("   2. sentence-transformers/all-mpnet-base-v2 (gratuito, mejor calidad, 768 dim)")
            print("   3. intfloat/e5-base-v2 (gratuito, excelente rendimiento, 768 dim)")
            print("   4. openai-ada-002 (de pago, requiere OpenAI API Key, 1536 dim)")
            
            model_choice = input("   Selecciona una opción (1-4) [1]: ").strip() or "1"
            
            models = {
                "1": "sentence-transformers/all-MiniLM-L6-v2",
                "2": "sentence-transformers/all-mpnet-base-v2",
                "3": "intfloat/e5-base-v2",
                "4": "openai-ada-002"
            }
            
            selected_model = models.get(model_choice, models["1"])
            content = content.replace(
                "EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2",
                f"EMBEDDING_MODEL={selected_model}"
            )
            
            # OpenAI API Key si es necesario
            if selected_model == "openai-ada-002":
                print("\n3. OPENAI API KEY (requerido para el modelo seleccionado)")
                print("   Obtén tu API key en: https://platform.openai.com/api-keys")
                openai_key = input("   Ingresa tu OpenAI API Key: ").strip()
                
                if openai_key:
                    content = content.replace("your_openai_api_key_here", openai_key)
            
            # Directorio de datos
            print("\n4. DIRECTORIO DE DATOS")
            data_dir = input(f"   Directorio de datos [{self.project_root / 'data' / 'raw'}]: ").strip()
            if data_dir:
                content = content.replace("DATA_DIRECTORY=data/raw", f"DATA_DIRECTORY={data_dir}")
            
            # Guardar archivo de configuración
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Archivo {self.config_file.name} creado correctamente ✓")
            
            # Mostrar advertencia de seguridad
            print("\n⚠️  IMPORTANTE:")
            print(f"   • El archivo {self.config_file.name} contiene claves API sensibles")
            print("   • NO lo subas a repositorios públicos")
            print("   • Añádelo a tu .gitignore")
            
            return True
            
        except Exception as e:
            logger.error(f"Error configurando archivo de entorno: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con Pinecone
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            # Cargar variables de entorno
            if self.config_file.exists():
                from dotenv import load_dotenv
                load_dotenv(self.config_file)
            
            pinecone_key = os.getenv('PINECONE_API_KEY')
            if not pinecone_key:
                logger.error("PINECONE_API_KEY no encontrada")
                return False
            
            # Probar conexión
            logger.info("Probando conexión con Pinecone...")
            
            from pinecone import Pinecone
            pc = Pinecone(api_key=pinecone_key)
            
            # Listar índices existentes
            indexes = pc.list_indexes()
            logger.info(f"Conexión exitosa ✓")
            logger.info(f"Índices existentes: {len(indexes.names())}")
            
            for index_name in indexes.names():
                logger.info(f"  - {index_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error probando conexión: {e}")
            return False
    
    def test_embedding_model(self) -> bool:
        """
        Prueba el modelo de embeddings
        
        Returns:
            bool: True si el modelo funciona correctamente
        """
        try:
            # Cargar configuración
            if self.config_file.exists():
                from dotenv import load_dotenv
                load_dotenv(self.config_file)
            
            model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            logger.info(f"Probando modelo de embeddings: {model_name}")
            
            if model_name.startswith('sentence-transformers/'):
                from sentence_transformers import SentenceTransformer
                
                model_path = model_name.replace('sentence-transformers/', '')
                model = SentenceTransformer(model_path)
                
                # Probar con texto de ejemplo
                test_text = "Constitución Política de los Estados Unidos Mexicanos"
                embedding = model.encode([test_text])
                
                logger.info(f"Embedding generado correctamente ✓")
                logger.info(f"Dimensión: {len(embedding[0])}")
                
            elif model_name == 'openai-ada-002':
                import openai
                
                openai_key = os.getenv('OPENAI_API_KEY')
                if not openai_key:
                    logger.error("OPENAI_API_KEY requerida para este modelo")
                    return False
                
                openai.api_key = openai_key
                
                # Probar con texto de ejemplo
                response = openai.Embedding.create(
                    input="Constitución Política de los Estados Unidos Mexicanos",
                    model="text-embedding-ada-002"
                )
                
                embedding = response['data'][0]['embedding']
                logger.info(f"Embedding de OpenAI generado correctamente ✓")
                logger.info(f"Dimensión: {len(embedding)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error probando modelo de embeddings: {e}")
            return False
    
    def create_data_directories(self) -> bool:
        """
        Crea los directorios necesarios para los datos
        
        Returns:
            bool: True si los directorios se crearon correctamente
        """
        try:
            data_root = self.project_root / "data"
            raw_data = data_root / "raw"
            
            # Crear directorios principales
            directories = [
                data_root,
                raw_data,
                raw_data / "cpeum",
                raw_data / "leyes_federales", 
                raw_data / "reglamentos_federales",
                raw_data / "dof",
                raw_data / "orden_juridico",
                self.project_root / "logs"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Directorio creado: {directory}")
            
            # Crear archivo .gitkeep para mantener directorios vacíos
            for directory in directories[2:6]:  # Solo para subdirectorios de raw
                gitkeep = directory / ".gitkeep"
                gitkeep.touch()
            
            logger.info("Estructura de directorios creada correctamente ✓")
            return True
            
        except Exception as e:
            logger.error(f"Error creando directorios: {e}")
            return False
    
    def show_next_steps(self):
        """Muestra los siguientes pasos después de la instalación"""
        print("\n" + "="*60)
        print("🎉 INSTALACIÓN COMPLETADA")
        print("="*60)
        
        print("\n📋 SIGUIENTES PASOS:")
        print("\n1. Extraer documentos legales:")
        print("   python scrape_cpeum.py")
        print("   python scrape_orden_juridico.py --file urls_leyes.txt")
        
        print("\n2. Configurar la base de datos vectorial:")
        print("   python setup_pinecone_vectordb.py --pinecone-key YOUR_KEY --create-index")
        
        print("\n3. Cargar documentos en la base de datos:")
        print("   python setup_pinecone_vectordb.py --pinecone-key YOUR_KEY --load-documents")
        
        print("\n4. Realizar búsquedas semánticas:")
        print("   python semantic_search.py \"derechos humanos constitución\"")
        print("   python semantic_search.py \"impuestos federales\" --category leyes_federales")
        
        print("\n📚 DOCUMENTACIÓN:")
        print("   • README_OrdenJuridico.md - Documentación del scraper")
        print("   • config_vectordb.env - Configuración de la base de datos")
        print("   • pinecone_vectordb.log - Logs del sistema")
        
        print("\n⚠️  RECORDATORIOS:")
        print("   • Mantén seguras tus API keys")
        print("   • El tier gratuito de Pinecone tiene límite de 2GB")
        print("   • Prioriza CPEUM > Leyes > Reglamentos > DOF")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Instalador automatizado para base de datos vectorial",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--check-python", action="store_true",
                       help="Verificar versión de Python")
    parser.add_argument("--install-deps", action="store_true",
                       help="Instalar dependencias")
    parser.add_argument("--setup-env", action="store_true",
                       help="Configurar archivo de entorno")
    parser.add_argument("--test-connection", action="store_true",
                       help="Probar conexión con Pinecone")
    parser.add_argument("--test-embeddings", action="store_true",
                       help="Probar modelo de embeddings")
    parser.add_argument("--create-dirs", action="store_true",
                       help="Crear directorios de datos")
    parser.add_argument("--full-setup", action="store_true",
                       help="Ejecutar configuración completa")
    
    args = parser.parse_args()
    
    installer = VectorDBInstaller()
    
    try:
        success = True
        
        if args.full_setup or args.check_python:
            print("\n🔍 Verificando versión de Python...")
            if not installer.check_python_version():
                success = False
        
        if success and (args.full_setup or args.create_dirs):
            print("\n📁 Creando estructura de directorios...")
            if not installer.create_data_directories():
                success = False
        
        if success and (args.full_setup or args.install_deps):
            print("\n📦 Instalando dependencias...")
            if not installer.install_dependencies():
                success = False
        
        if success and (args.full_setup or args.setup_env):
            print("\n⚙️  Configurando variables de entorno...")
            if not installer.setup_environment_file():
                success = False
        
        if success and (args.full_setup or args.test_connection):
            print("\n🔗 Probando conexión con Pinecone...")
            if not installer.test_connection():
                success = False
        
        if success and (args.full_setup or args.test_embeddings):
            print("\n🧠 Probando modelo de embeddings...")
            if not installer.test_embedding_model():
                success = False
        
        if success:
            if args.full_setup:
                installer.show_next_steps()
            else:
                print("\n✅ Operación completada exitosamente")
        else:
            print("\n❌ La instalación falló. Revisa los errores anteriores.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()