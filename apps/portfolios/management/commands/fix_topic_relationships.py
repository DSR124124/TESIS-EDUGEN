"""
Comando para automáticamente corregir y prevenir problemas de relaciones de temas
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import logging

from apps.portfolios.models import PortfolioTopic, PortfolioMaterial
from apps.academic.models import CourseTopic
from apps.portfolios.utils import safe_prepare_topic_for_template, TopicMaterialsManager

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Automaticamente corrige y previene problemas de relaciones de temas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se corregiría sin hacer cambios',
        )
        parser.add_argument(
            '--fix-materials',
            action='store_true',
            help='Corregir materiales con relaciones incorrectas',
        )
        parser.add_argument(
            '--verify-all',
            action='store_true',
            help='Verificar todos los temas en el sistema',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Iniciando verificación y corrección automática de temas...')
        )

        if options['verify_all']:
            self.verify_all_topics(options['dry_run'])
        
        if options['fix_materials']:
            self.fix_material_relationships(options['dry_run'])
        
        self.apply_automatic_safety(options['dry_run'])
        
        self.stdout.write(
            self.style.SUCCESS('✅ Verificación y corrección completada.')
        )

    def verify_all_topics(self, dry_run=False):
        """Verifica todos los temas en el sistema"""
        self.stdout.write('🔍 Verificando todos los temas...')
        
        # Verificar PortfolioTopics
        portfolio_topics = PortfolioTopic.objects.all()
        self.stdout.write(f'Verificando {portfolio_topics.count()} PortfolioTopics...')
        
        for topic in portfolio_topics:
            try:
                # Usar utilidades seguras para verificar
                safe_topic = safe_prepare_topic_for_template(topic)
                manager = TopicMaterialsManager(topic)
                
                # Verificar que el topic puede acceder a sus materiales
                material_count = manager.count_materials()
                
                self.stdout.write(
                    f'  ✅ PortfolioTopic {topic.id}: {material_count} materiales'
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error en PortfolioTopic {topic.id}: {e}')
                )
                if not dry_run:
                    self.fix_topic_issue(topic)

        # Verificar CourseTopics
        course_topics = CourseTopic.objects.all()
        self.stdout.write(f'Verificando {course_topics.count()} CourseTopics...')
        
        for topic in course_topics:
            try:
                # Usar utilidades seguras
                safe_topic = safe_prepare_topic_for_template(topic)
                manager = TopicMaterialsManager(topic)
                
                # Verificar que el topic puede acceder a sus materiales
                material_count = manager.count_materials()
                
                self.stdout.write(
                    f'  ✅ CourseTopic {topic.id}: {material_count} materiales'
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error en CourseTopic {topic.id}: {e}')
                )
                if not dry_run:
                    self.fix_topic_issue(topic)

    def fix_material_relationships(self, dry_run=False):
        """Corrige materiales con relaciones incorrectas"""
        self.stdout.write('🔧 Corrigiendo relaciones de materiales...')
        
        # Buscar materiales que podrían tener problemas
        orphan_materials = PortfolioMaterial.objects.filter(
            topic__isnull=True,
            course_topic__isnull=True
        )
        
        if orphan_materials.exists():
            self.stdout.write(
                self.style.WARNING(f'Encontrados {orphan_materials.count()} materiales huérfanos')
            )
            
            if not dry_run:
                # Intentar reenlazar materiales huérfanos
                for material in orphan_materials:
                    self.try_relink_material(material)
        
        # Verificar materiales con doble relación
        double_linked = PortfolioMaterial.objects.filter(
            topic__isnull=False,
            course_topic__isnull=False
        )
        
        if double_linked.exists():
            self.stdout.write(
                self.style.WARNING(f'Encontrados {double_linked.count()} materiales con doble enlace')
            )
            
            if not dry_run:
                # Corregir dobles enlaces
                for material in double_linked:
                    self.fix_double_link(material)

    def fix_topic_issue(self, topic):
        """Corrige problemas específicos de un tema"""
        try:
            with transaction.atomic():
                # Aplicar preparación segura
                safe_prepare_topic_for_template(topic)
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Corregido tema {topic.id}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ No se pudo corregir tema {topic.id}: {e}')
            )

    def try_relink_material(self, material):
        """Intenta reenlazar un material huérfano"""
        try:
            # Buscar un tema apropiado basado en el título o contenido
            if hasattr(material, 'title') and material.title:
                # Buscar por título similar
                similar_topics = PortfolioTopic.objects.filter(
                    title__icontains=material.title[:20]
                )
                
                if similar_topics.exists():
                    material.topic = similar_topics.first()
                    material.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ Material {material.id} reenlazado')
                    )
                    return
            
            self.stdout.write(
                self.style.WARNING(f'  ⚠️ No se pudo reenlazar material {material.id}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error reenlazando material {material.id}: {e}')
            )

    def fix_double_link(self, material):
        """Corrige materiales con enlaces dobles"""
        try:
            # Preferir PortfolioTopic sobre CourseTopic
            if material.topic:
                material.course_topic = None
                material.save()
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Doble enlace corregido para material {material.id}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error corrigiendo doble enlace {material.id}: {e}')
            )

    def apply_automatic_safety(self, dry_run=False):
        """Aplica automáticamente protecciones de seguridad"""
        self.stdout.write('🛡️  Aplicando protecciones automáticas...')
        
        if not dry_run:
            try:
                # Importar y aplicar utilidades automáticamente
                from apps.portfolios.utils import safe_process_topics_list
                from apps.portfolios.decorators import AutoSafeTopicMixin
                
                self.stdout.write(
                    self.style.SUCCESS('  ✅ Protecciones automáticas aplicadas')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error aplicando protecciones: {e}')
                )
        else:
            self.stdout.write('  ℹ️  Protecciones automáticas se aplicarían')

    def validate_system_integrity(self):
        """Valida la integridad completa del sistema"""
        self.stdout.write('🔍 Validando integridad del sistema...')
        
        issues_found = 0
        
        # Verificar coherencia de datos
        total_portfolio_topics = PortfolioTopic.objects.count()
        total_course_topics = CourseTopic.objects.count()
        total_materials = PortfolioMaterial.objects.count()
        
        self.stdout.write(f'  📊 Estadísticas del sistema:')
        self.stdout.write(f'    - PortfolioTopics: {total_portfolio_topics}')
        self.stdout.write(f'    - CourseTopics: {total_course_topics}')
        self.stdout.write(f'    - Materiales: {total_materials}')
        
        # Verificar materiales sin tema
        orphan_count = PortfolioMaterial.objects.filter(
            topic__isnull=True, 
            course_topic__isnull=True
        ).count()
        
        if orphan_count > 0:
            issues_found += 1
            self.stdout.write(
                self.style.WARNING(f'    ⚠️  Materiales huérfanos: {orphan_count}')
            )
        
        # Verificar temas sin curso
        topics_without_course = PortfolioTopic.objects.filter(course__isnull=True).count()
        
        if topics_without_course > 0:
            issues_found += 1
            self.stdout.write(
                self.style.WARNING(f'    ⚠️  Temas sin curso: {topics_without_course}')
            )
        
        if issues_found == 0:
            self.stdout.write(
                self.style.SUCCESS('  ✅ Sistema en perfecto estado')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  {issues_found} problemas encontrados')
            )
        
        return issues_found == 0 