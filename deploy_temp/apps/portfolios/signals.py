from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
import logging

from apps.academic.models import Enrollment, CourseAssignment, CourseTopic
from .models import StudentPortfolio, PortfolioTopic, PortfolioMaterial
from .utils import safe_prepare_topic_for_template

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Enrollment)
def auto_assign_topics_and_materials(sender, instance, created, **kwargs):
    """
    Automáticamente asigna temas y materiales existentes a estudiantes nuevos
    basado en su grado, sección y cursos asignados.
    """
    # Solo procesar si es una nueva matrícula activa
    if not created or instance.status != 'ACTIVE':
        return
        
    try:
        with transaction.atomic():
            student = instance.student
            section = instance.section
            current_month = timezone.now().month
            current_year = timezone.now().year
            academic_year = str(current_year)
            
            logger.info(f"🎓 Procesando asignación automática para nuevo estudiante: {student.user.get_full_name()} en sección {section.name}")
            
            # 1. Crear o obtener el portafolio mensual del estudiante
            portfolio, portfolio_created = StudentPortfolio.objects.get_or_create(
                student=student,
                month=current_month,
                academic_year=academic_year
            )
            
            if portfolio_created:
                logger.info(f"📁 Portafolio creado para {student.user.get_full_name()}")
            
            # 2. Obtener todos los cursos asignados a la sección del estudiante
            course_assignments = CourseAssignment.objects.filter(
                section=section,
                is_active=True
            )
            
            topics_created = 0
            materials_copied = 0
            
            for assignment in course_assignments:
                course = assignment.course
                teacher = assignment.teacher
                
                logger.info(f"📚 Procesando curso: {course.name} con profesor: {teacher.user.get_full_name()}")
                
                # 3. Buscar CourseTopics existentes para este curso y profesor
                existing_course_topics = CourseTopic.objects.filter(
                    course=course,
                    teacher=teacher,
                    section=section,  # Solo temas de la misma sección
                    is_active=True
                )
                
                for course_topic in existing_course_topics:
                    # Crear PortfolioTopic correspondiente si no existe
                    portfolio_topic, topic_created = PortfolioTopic.objects.get_or_create(
                        portfolio=portfolio,
                        course=course,
                        teacher=teacher,
                        title=course_topic.title,
                        defaults={
                            'description': course_topic.description or f"Tema: {course_topic.title}",
                            'is_complete': False,
                            'last_updated_by': teacher.user
                        }
                    )
                    
                    if topic_created:
                        topics_created += 1
                        logger.info(f"  ✅ Tema creado: {course_topic.title}")
                        
                        # 4. Copiar materiales de clase del CourseTopic
                        # SOLO copiar materiales que realmente pertenecen a este CourseTopic específico
                        course_materials = PortfolioMaterial.objects.filter(
                            course_topic=course_topic,
                            is_class_material=True
                        )
                        
                        for course_material in course_materials:
                            # Verificar si ya existe este material EXACTO en el portafolio del estudiante
                            existing_material = PortfolioMaterial.objects.filter(
                                topic=portfolio_topic,
                                title=course_material.title,
                                material_type=course_material.material_type,
                                course_topic=course_topic  # CRÍTICO: verificar que pertenece al mismo CourseTopic
                            ).first()
                            
                            if not existing_material:
                                # Crear una copia del material para el estudiante
                                new_material = PortfolioMaterial.objects.create(
                                    topic=portfolio_topic,
                                    course_topic=course_topic,  # CRÍTICO: mantener la relación correcta
                                    title=course_material.title,
                                    description=course_material.description,
                                    material_type=course_material.material_type,
                                    file=course_material.file,  # Referencia al mismo archivo
                                    scorm_package=course_material.scorm_package,
                                    ai_generated=course_material.ai_generated,
                                    is_class_material=True  # Mantener como material de clase
                                )
                                materials_copied += 1
                                logger.info(f"    📄 Material copiado: {course_material.title}")
                
                # 5. NUEVA LÓGICA: Buscar PortfolioTopics existentes CON MAYOR ESPECIFICIDAD
                # Solo buscar temas que coincidan EXACTAMENTE en curso, profesor Y sección
                existing_portfolio_topics = PortfolioTopic.objects.filter(
                    course=course,
                    teacher=teacher,
                    portfolio__student__enrollments__section=section,
                    portfolio__student__enrollments__status='ACTIVE'
                ).exclude(
                    portfolio=portfolio  # Excluir el portafolio del estudiante actual
                ).distinct()
                
                for existing_topic in existing_portfolio_topics:
                    # Crear el mismo tema para el nuevo estudiante si no existe
                    portfolio_topic, topic_created = PortfolioTopic.objects.get_or_create(
                        portfolio=portfolio,
                        course=course,
                        teacher=teacher,
                        title=existing_topic.title,
                        defaults={
                            'description': existing_topic.description,
                            'is_complete': False,
                            'last_updated_by': teacher.user
                        }
                    )
                    
                    if topic_created:
                        topics_created += 1
                        logger.info(f"  ✅ Tema replicado: {existing_topic.title}")
                        
                        # MEJORAR: Solo copiar materiales de clase que realmente pertenecen a este tema
                        class_materials = existing_topic.materials.filter(
                            is_class_material=True,
                            # AGREGAR: Verificar que el material sea específico para este tema/curso
                            topic__course=course,
                            topic__teacher=teacher
                        )
                        
                        for class_material in class_materials:
                            # Verificar si ya existe CON MAYOR ESPECIFICIDAD
                            existing_material = PortfolioMaterial.objects.filter(
                                topic=portfolio_topic,
                                title=class_material.title,
                                material_type=class_material.material_type,
                                # AGREGAR: Verificar también la fecha para evitar duplicados recientes
                                created_at__date__gte=(timezone.now() - timezone.timedelta(days=1)).date()
                            ).first()
                            
                            if not existing_material:
                                # Crear copia del material CON VALIDACIÓN
                                try:
                                    new_material = PortfolioMaterial.objects.create(
                                        topic=portfolio_topic,
                                        title=class_material.title,
                                        description=class_material.description,
                                        material_type=class_material.material_type,
                                        file=class_material.file,
                                        scorm_package=class_material.scorm_package,
                                        ai_generated=class_material.ai_generated,
                                        is_class_material=True
                                    )
                                    materials_copied += 1
                                    logger.info(f"    📄 Material de clase copiado: {class_material.title}")
                                except Exception as e:
                                    logger.error(f"    ❌ Error copiando material {class_material.title}: {str(e)}")
                                    continue
            
            # Log del resumen
            logger.info(f"🎉 Asignación automática completada para {student.user.get_full_name()}:")
            logger.info(f"   📝 Temas creados: {topics_created}")
            logger.info(f"   📄 Materiales copiados: {materials_copied}")
            
            # Crear un registro de log para el administrador
            if topics_created > 0 or materials_copied > 0:
                logger.info(
                    f"ASIGNACIÓN AUTOMÁTICA - Estudiante: {student.user.get_full_name()} "
                    f"({student.dni}) agregado a sección {section.grade.name}-{section.name}. "
                    f"Creados {topics_created} temas y copiados {materials_copied} materiales."
                )
            
    except Exception as e:
        logger.error(f"❌ Error en asignación automática para {student.user.get_full_name()}: {str(e)}")
        # No re-lanzar la excepción para evitar que falle la creación del estudiante

@receiver(post_save, sender=CourseTopic)
def auto_replicate_course_topic_to_students(sender, instance, created, **kwargs):
    """
    Cuando un profesor crea un nuevo CourseTopic, automáticamente lo replica
    a todos los estudiantes activos de la sección correspondiente.
    """
    if not created or not instance.is_active:
        return
    
    try:
        with transaction.atomic():
            course_topic = instance
            section = course_topic.section
            course = course_topic.course
            teacher = course_topic.teacher
            
            logger.info(f"📚 Replicando nuevo CourseTopic '{course_topic.title}' a estudiantes de la sección {section.name}")
            
            # Obtener todos los estudiantes activos de la sección
            active_enrollments = Enrollment.objects.filter(
                section=section,
                status='ACTIVE'
            ).select_related('student')
            
            current_month = timezone.now().month
            current_year = timezone.now().year
            academic_year = str(current_year)
            
            topics_created = 0
            
            for enrollment in active_enrollments:
                student = enrollment.student
                
                # Obtener o crear el portafolio del estudiante
                portfolio, _ = StudentPortfolio.objects.get_or_create(
                    student=student,
                    month=current_month,
                    academic_year=academic_year
                )
                
                # Crear el PortfolioTopic correspondiente
                portfolio_topic, topic_created = PortfolioTopic.objects.get_or_create(
                    portfolio=portfolio,
                    course=course,
                    teacher=teacher,
                    title=course_topic.title,
                    defaults={
                        'description': course_topic.description or f"Tema: {course_topic.title}",
                        'is_complete': False,
                        'last_updated_by': teacher.user
                    }
                )
                
                if topic_created:
                    topics_created += 1
                    logger.info(f"  ✅ Tema creado para {student.user.get_full_name()}: {course_topic.title}")
            
            logger.info(f"🎉 Replicación completada: {topics_created} temas creados para CourseTopic '{course_topic.title}'")
            
    except Exception as e:
        logger.error(f"❌ Error replicando CourseTopic {instance.title}: {str(e)}")

def manually_sync_student_with_section(student, section):
    """
    Función auxiliar para sincronizar manualmente un estudiante con su sección.
    Útil para estudiantes que fueron agregados antes de implementar el sistema automático.
    """
    try:
        with transaction.atomic():
            logger.info(f"🔄 Sincronización manual iniciada para {student.user.get_full_name()} en sección {section.name}")
            
            # Simular una nueva matrícula para activar el sistema automático
            enrollment = Enrollment.objects.filter(student=student, section=section, status='ACTIVE').first()
            
            if enrollment:
                # Llamar manualmente la función de asignación automática
                auto_assign_topics_and_materials(Enrollment, enrollment, created=True)
                logger.info(f"✅ Sincronización manual completada para {student.user.get_full_name()}")
                return True
            else:
                logger.warning(f"⚠️ No se encontró matrícula activa para {student.user.get_full_name()} en sección {section.name}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error en sincronización manual: {str(e)}")
        return False 