from django.db.models import Count
from django.utils import timezone
import logging

from .models import PortfolioTopic

logger = logging.getLogger(__name__)

def clean_duplicate_portfolio_topics():
    """
    Función de utilidad para limpiar temas duplicados en portafolios.
    Mantiene el tema más reciente cuando hay duplicados exactos.
    """
    try:
        # Buscar grupos de temas duplicados (mismo portfolio, course, teacher, title)
        duplicates = (PortfolioTopic.objects
                     .values('portfolio', 'course', 'teacher', 'title')
                     .annotate(count=Count('id'))
                     .filter(count__gt=1))
        
        cleaned_count = 0
        for duplicate_group in duplicates:
            # Obtener todos los temas duplicados en este grupo
            duplicate_topics = PortfolioTopic.objects.filter(
                portfolio=duplicate_group['portfolio'],
                course=duplicate_group['course'],
                teacher=duplicate_group['teacher'],
                title=duplicate_group['title']
            ).order_by('-created_at')  # Más reciente primero
            
            # Mantener solo el más reciente
            topics_to_delete = duplicate_topics[1:]  # Todos excepto el primero (más reciente)
            
            for topic_to_delete in topics_to_delete:
                # Mover materiales del tema duplicado al tema principal si no existen ya
                main_topic = duplicate_topics.first()
                for material in topic_to_delete.materials.all():
                    # Verificar si ya existe un material similar en el tema principal
                    existing_material = main_topic.materials.filter(
                        title=material.title,
                        material_type=material.material_type
                    ).first()
                    
                    if not existing_material:
                        # Mover el material al tema principal
                        material.topic = main_topic
                        material.save()
                
                # Eliminar el tema duplicado
                topic_to_delete.delete()
                cleaned_count += 1
        
        if cleaned_count > 0:
            logger.info(f"Limpieza de duplicados completada: {cleaned_count} temas duplicados eliminados")
        
        return cleaned_count
    except Exception as e:
        logger.error(f"Error durante la limpieza de duplicados: {str(e)}")
        return 0 

class TopicMaterialsManager:
    """
    Manager seguro para manejar materiales de temas, 
    independientemente de si son PortfolioTopic o CourseTopic
    """
    
    def __init__(self, topic):
        self.topic = topic
        self._is_portfolio_topic = hasattr(topic, 'portfolio')
        self._is_course_topic = hasattr(topic, 'section')
        
    @property
    def is_portfolio_topic(self):
        """Verifica si es un PortfolioTopic"""
        return self._is_portfolio_topic
    
    @property
    def is_course_topic(self):
        """Verifica si es un CourseTopic"""
        return self._is_course_topic
    
    def get_materials(self):
        """Obtiene materiales de forma segura"""
        if self.is_portfolio_topic:
            return self.topic.materials.all()
        elif self.is_course_topic:
            # Para CourseTopic, buscar materiales en PortfolioMaterial.course_topic
            from apps.portfolios.models import PortfolioMaterial
            return PortfolioMaterial.objects.filter(course_topic=self.topic)
        else:
            return []
    
    def count_materials(self):
        """Cuenta materiales de forma segura"""
        if self.is_portfolio_topic:
            return self.topic.materials.count()
        elif self.is_course_topic:
            from apps.portfolios.models import PortfolioMaterial
            return PortfolioMaterial.objects.filter(course_topic=self.topic).count()
        else:
            return 0
    
    def filter_materials(self, **kwargs):
        """Filtra materiales de forma segura"""
        if self.is_portfolio_topic:
            return self.topic.materials.filter(**kwargs)
        elif self.is_course_topic:
            from apps.portfolios.models import PortfolioMaterial
            return PortfolioMaterial.objects.filter(course_topic=self.topic, **kwargs)
        else:
            return []
    
    def materials_exist(self):
        """Verifica si existen materiales de forma segura"""
        if self.is_portfolio_topic:
            return self.topic.materials.exists()
        elif self.is_course_topic:
            from apps.portfolios.models import PortfolioMaterial
            return PortfolioMaterial.objects.filter(course_topic=self.topic).exists()
        else:
            return False

def safe_get_topic_materials(topic):
    """
    Función segura para obtener materiales de cualquier tipo de tema
    Evita automáticamente errores de asignación de relaciones
    """
    manager = TopicMaterialsManager(topic)
    return manager.get_materials()

def safe_count_topic_materials(topic):
    """
    Función segura para contar materiales de cualquier tipo de tema
    """
    manager = TopicMaterialsManager(topic)
    return manager.count_materials()

def safe_prepare_topic_for_template(topic):
    """
    Prepara automáticamente un tema para uso en templates
    Evita errores de relaciones y configura atributos necesarios
    """
    # Identificar el tipo de tema
    if hasattr(topic, 'portfolio'):
        topic.topic_type = 'portfolio'
        topic.materials_count = topic.materials.count()
    elif hasattr(topic, 'section'):
        topic.topic_type = 'course'
        topic.materials_count = safe_count_topic_materials(topic)
        # Agregar atributo portfolio como None para compatibilidad de template
        topic.portfolio = None
        # Simular campo is_complete para CourseTopics
        if not hasattr(topic, 'is_complete'):
            topic.is_complete = False
    else:
        logger.warning(f"Tipo de tema desconocido: {type(topic)}")
        topic.topic_type = 'unknown'
        topic.materials_count = 0
        topic.portfolio = None
        topic.is_complete = False
    
    return topic

def safe_process_topics_list(topics):
    """
    Procesa una lista de temas de forma segura
    Evita automáticamente errores de relaciones para todos los elementos
    """
    processed_topics = []
    for topic in topics:
        try:
            processed_topic = safe_prepare_topic_for_template(topic)
            processed_topics.append(processed_topic)
        except Exception as e:
            logger.error(f"Error procesando tema {getattr(topic, 'id', 'unknown')}: {e}")
            # Continuar con el siguiente tema en lugar de fallar completamente
            continue
    
    return processed_topics

def get_unified_topic_context(topic):
    """
    Genera un contexto unificado para cualquier tipo de tema
    Maneja automáticamente las diferencias entre PortfolioTopic y CourseTopic
    """
    context = {}
    manager = TopicMaterialsManager(topic)
    
    # Información básica del tema
    context['topic'] = topic
    context['is_portfolio_topic'] = manager.is_portfolio_topic
    context['is_course_topic'] = manager.is_course_topic
    
    # Materiales del tema
    context['materials'] = manager.get_materials()
    context['materials_count'] = manager.count_materials()
    context['has_materials'] = manager.materials_exist()
    
    # Clasificación de materiales
    context['ai_materials'] = manager.filter_materials(ai_generated=True)
    context['regular_materials'] = manager.filter_materials(ai_generated=False)
    context['class_materials'] = manager.filter_materials(is_class_material=True)
    context['personal_materials'] = manager.filter_materials(is_class_material=False)
    
    # Contadores
    context['ai_materials_count'] = context['ai_materials'].count()
    context['regular_materials_count'] = context['regular_materials'].count()
    context['class_materials_count'] = context['class_materials'].count()
    context['personal_materials_count'] = context['personal_materials'].count()
    
    return context

class SafeTopicProxy:
    """
    Proxy que envuelve un tema y previene automáticamente errores de relaciones
    """
    
    def __init__(self, topic):
        self._topic = topic
        self._manager = TopicMaterialsManager(topic)
    
    def __getattr__(self, name):
        # Si es una propiedad de materials, usar el manager seguro
        if name == 'materials':
            return self._get_safe_materials_manager()
        
        # Para cualquier otra propiedad, usar el tema original
        return getattr(self._topic, name)
    
    def _get_safe_materials_manager(self):
        """Retorna un manager seguro que no puede ser asignado"""
        class SafeMaterialsManager:
            def __init__(self, manager):
                self._manager = manager
            
            def all(self):
                return self._manager.get_materials()
            
            def count(self):
                return self._manager.count_materials()
            
            def filter(self, **kwargs):
                return self._manager.filter_materials(**kwargs)
            
            def exists(self):
                return self._manager.materials_exist()
            
            def __setattr__(self, name, value):
                if name.startswith('_'):
                    super().__setattr__(name, value)
                else:
                    raise AttributeError(
                        "Direct assignment to the reverse side of a related set is prohibited. "
                        "This is automatically prevented by SafeTopicProxy."
                    )
        
        return SafeMaterialsManager(self._manager)

def make_topic_safe(topic):
    """
    Convierte un tema en un proxy seguro que previene errores automáticamente
    """
    return SafeTopicProxy(topic) 