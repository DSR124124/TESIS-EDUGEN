import os
import zipfile
import tempfile
import shutil
import xml.etree.ElementTree as ET

class SCORMValidator:
    """
    Clase para validar la estructura y contenido de un paquete SCORM.
    """
    
    def __init__(self, package_path):
        self.package_path = package_path
        self.temp_dir = None
        
    def validate(self):
        """
        Valida un paquete SCORM y devuelve el resultado.
        
        Returns:
            dict: Resultado de la validación con errores, advertencias y estado
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Verificar que el archivo existe
        if not os.path.exists(self.package_path):
            result['is_valid'] = False
            result['errors'].append('El archivo no existe')
            return result
        
        # Verificar que es un ZIP válido
        if not zipfile.is_zipfile(self.package_path):
            result['is_valid'] = False
            result['errors'].append('El archivo no es un ZIP válido')
            return result
        
        # Extraer y validar el contenido
        self.temp_dir = tempfile.mkdtemp()
        
        try:
            with zipfile.ZipFile(self.package_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # Verificar la existencia del manifiesto
            manifest_path = os.path.join(self.temp_dir, 'imsmanifest.xml')
            if not os.path.exists(manifest_path):
                result['is_valid'] = False
                result['errors'].append('No se encontró el archivo imsmanifest.xml')
                return result
            
            # Validar el manifiesto
            manifest_validation = self._validate_manifest(manifest_path)
            if not manifest_validation['is_valid']:
                result['is_valid'] = False
                result['errors'].extend(manifest_validation['errors'])
            result['warnings'].extend(manifest_validation['warnings'])
            
            # Validar archivos requeridos
            files_validation = self._validate_required_files(self.temp_dir)
            if not files_validation['is_valid']:
                result['is_valid'] = False
                result['errors'].extend(files_validation['errors'])
            result['warnings'].extend(files_validation['warnings'])
            
            return result
        finally:
            # Limpiar archivos temporales
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    def _validate_manifest(self, manifest_path):
        """
        Valida el archivo imsmanifest.xml
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            
            # Verificar elementos requeridos
            namespaces = {
                'imscp': 'http://www.imsglobal.org/xsd/imscp_v1p1',
                'adlcp': 'http://www.adlnet.org/xsd/adlcp_v1p3'
            }
            
            # Verificar organizations
            organizations = root.findall('./imscp:organizations', namespaces)
            if not organizations:
                result['is_valid'] = False
                result['errors'].append('El manifiesto no contiene el elemento <organizations>')
            
            # Verificar resources
            resources = root.findall('./imscp:resources', namespaces)
            if not resources:
                result['is_valid'] = False
                result['errors'].append('El manifiesto no contiene el elemento <resources>')
            
            # Otras validaciones según la versión SCORM
            # (Simplificado para este ejemplo)
            
        except ET.ParseError:
            result['is_valid'] = False
            result['errors'].append('El archivo imsmanifest.xml no es un XML válido')
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f'Error al validar el manifiesto: {str(e)}')
        
        return result
    
    def _validate_required_files(self, package_dir):
        """
        Valida que existan los archivos requeridos según el manifiesto
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Verificar index.html o similar
        index_file = os.path.join(package_dir, 'index.html')
        if not os.path.exists(index_file):
            result['warnings'].append('No se encontró un archivo index.html')
        
        # Verificar API de SCORM
        scorm_api_file = os.path.join(package_dir, 'scorm_api.js')
        if not os.path.exists(scorm_api_file):
            result['warnings'].append('No se encontró el archivo scorm_api.js')
        
        return result 