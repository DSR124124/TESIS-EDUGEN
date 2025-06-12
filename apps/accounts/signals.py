from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Teacher

@receiver(post_save, sender=Teacher)
def create_academic_teacher(sender, instance, created, **kwargs):
    """
    Cada vez que se crea o actualiza un Teacher en la app accounts,
    se sincronizará con la app academic.
    """
    from apps.academic.models import Teacher as AcademicTeacher
    
    # Verificar si el profesor ya existe en la app academic
    try:
        academic_teacher = AcademicTeacher.objects.get(user=instance.user)
        # Actualizar datos si ya existe
        academic_teacher.dni = instance.dni
        academic_teacher.phone = instance.phone
        academic_teacher.address = instance.address
        academic_teacher.teacher_code = instance.teacher_code
        academic_teacher.is_active = instance.is_active
        academic_teacher.save()
        print(f"Updated academic teacher: {academic_teacher}")
    except AcademicTeacher.DoesNotExist:
        # Crear nuevo profesor en academic si no existe
        academic_teacher = AcademicTeacher.objects.create(
            user=instance.user,
            dni=instance.dni,
            speciality='MAT',  # Default a Matemática
            phone=instance.phone,
            address=instance.address,
            teacher_code=instance.teacher_code,
            is_active=instance.is_active
        )
        print(f"Created new academic teacher: {academic_teacher}") 