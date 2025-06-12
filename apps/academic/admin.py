from django.contrib import admin
from .models import Course, Teacher, Student, Grade, Section, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')
    ordering = ('code',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'dni', 'speciality', 'is_active')
    list_filter = ('speciality', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'dni')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'dni', 'guardian_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__first_name', 'user__last_name', 'dni', 'guardian_name')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'is_active', 'created_at')
    list_filter = ('level', 'is_active')
    search_fields = ('name',)
    ordering = ('level', 'name')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'capacity', 'current_students', 'is_active')
    list_filter = ('grade', 'is_active')
    search_fields = ('name', 'grade__name')
    ordering = ('grade', 'name')
    list_editable = ('capacity', 'is_active')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('grade', 'name')
        return ()

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'section', 'academic_year', 'status', 'enrollment_date')
    list_filter = ('status', 'academic_year', 'section__grade')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__dni', 'section__name', 'section__grade__name')
    date_hierarchy = 'enrollment_date'
    raw_id_fields = ('student', 'section')
