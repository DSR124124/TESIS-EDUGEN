import requests
import logging
import os
from dotenv import load_dotenv
from django.conf import settings

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

class ImageSearchService:
    """
    Servicio para buscar imágenes usando APIs gratuitas como Pexels y Pixabay
    """
    
    def __init__(self):
        # Configuración para Pexels
        self.pexels_api_key = os.environ.get('PEXELS_API_KEY', '')
        # Configuración para Pixabay
        self.pixabay_api_key = os.environ.get('PIXABAY_API_KEY', '')
        
        # Determinar qué API usar según las claves disponibles
        self.use_pexels = bool(self.pexels_api_key)
        self.use_pixabay = bool(self.pixabay_api_key)
    
    def search_images(self, query, per_page=5, page=1):
        """
        Busca imágenes relacionadas con el query en las APIs disponibles
        Retorna una lista de imágenes con formato estandarizado
        """
        results = []
        
        if self.use_pexels:
            pexels_results = self._search_pexels(query, per_page, page)
            if pexels_results:
                results.extend(pexels_results)
        
        if self.use_pixabay and len(results) < per_page:
            # Solo usamos Pixabay si necesitamos más resultados
            need_more = per_page - len(results)
            pixabay_results = self._search_pixabay(query, need_more, page)
            if pixabay_results:
                results.extend(pixabay_results)
        
        return results[:per_page]  # Asegurar que no excedemos el número solicitado
    
    def _search_pexels(self, query, per_page=5, page=1):
        """
        Busca imágenes en la API de Pexels
        """
        try:
            headers = {"Authorization": self.pexels_api_key}
            response = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": query, "per_page": per_page, "page": page},
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Error en la API de Pexels: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            
            # Convertir al formato estandarizado
            results = []
            for photo in data.get("photos", []):
                results.append({
                    "id": photo["id"],
                    "thumbnail": photo["src"]["small"],
                    "preview": photo["src"]["medium"],
                    "full_url": photo["src"]["original"],
                    "width": photo["width"],
                    "height": photo["height"],
                    "source": "pexels",
                    "source_url": photo["url"],
                    "photographer": photo["photographer"],
                    "alt_text": photo.get("alt", query)
                })
            
            return results
            
        except Exception as e:
            logger.exception(f"Error al buscar en Pexels: {str(e)}")
            return []
    
    def _search_pixabay(self, query, per_page=5, page=1):
        """
        Busca imágenes en la API de Pixabay
        """
        try:
            response = requests.get(
                "https://pixabay.com/api/",
                params={
                    "key": self.pixabay_api_key,
                    "q": query,
                    "per_page": per_page,
                    "page": page,
                    "image_type": "photo"
                },
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Error en la API de Pixabay: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            
            # Convertir al formato estandarizado
            results = []
            for hit in data.get("hits", []):
                results.append({
                    "id": hit["id"],
                    "thumbnail": hit["previewURL"],
                    "preview": hit["webformatURL"],
                    "full_url": hit["largeImageURL"],
                    "width": hit["imageWidth"],
                    "height": hit["imageHeight"],
                    "source": "pixabay",
                    "source_url": hit["pageURL"],
                    "photographer": hit["user"],
                    "alt_text": query
                })
            
            return results
            
        except Exception as e:
            logger.exception(f"Error al buscar en Pixabay: {str(e)}")
            return []

# Instancia singleton para usar en toda la aplicación
image_service = ImageSearchService() 