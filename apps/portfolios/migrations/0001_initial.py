# Generated by Django 4.2.20 on 2025-04-17 23:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("scorm_packager", "0001_initial"),
        ("academic", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentPortfolio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "academic_year",
                    models.CharField(
                        default="2025", max_length=9, verbose_name="Año Académico"
                    ),
                ),
                (
                    "month",
                    models.IntegerField(
                        choices=[
                            (1, "Enero"),
                            (2, "Febrero"),
                            (3, "Marzo"),
                            (4, "Abril"),
                            (5, "Mayo"),
                            (6, "Junio"),
                            (7, "Julio"),
                            (8, "Agosto"),
                            (9, "Septiembre"),
                            (10, "Octubre"),
                            (11, "Noviembre"),
                            (12, "Diciembre"),
                        ],
                        verbose_name="Mes",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="portfolios",
                        to="academic.student",
                        verbose_name="Estudiante",
                    ),
                ),
            ],
            options={
                "verbose_name": "Portafolio de Estudiante",
                "verbose_name_plural": "Portafolios de Estudiantes",
                "ordering": ["academic_year", "month", "student"],
                "unique_together": {("student", "academic_year", "month")},
            },
        ),
        migrations.CreateModel(
            name="PortfolioTopic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=200, verbose_name="Título del Tema"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Descripción del Tema"),
                ),
                (
                    "is_complete",
                    models.BooleanField(default=False, verbose_name="Completado"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="portfolio_topics",
                        to="academic.course",
                        verbose_name="Curso",
                    ),
                ),
                (
                    "last_updated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="updated_portfolio_topics",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Última actualización por",
                    ),
                ),
                (
                    "portfolio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="portfolio_topics",
                        to="portfolios.studentportfolio",
                        verbose_name="Portafolio",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="portfolio_topics",
                        to="academic.teacher",
                        verbose_name="Profesor",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tema de Portafolio",
                "verbose_name_plural": "Temas de Portafolio",
                "ordering": ["portfolio", "course", "created_at"],
            },
        ),
        migrations.CreateModel(
            name="PortfolioMaterial",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Título")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Descripción"),
                ),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="portfolio_materials/%Y/%m/",
                        verbose_name="Archivo",
                    ),
                ),
                (
                    "material_type",
                    models.CharField(
                        choices=[
                            ("EJERCICIO", "Ejercicio"),
                            ("TAREA", "Tarea"),
                            ("EXAMEN", "Examen"),
                            ("PROYECTO", "Proyecto"),
                            ("LECTURA", "Lectura"),
                            ("OTRO", "Otro"),
                            ("SCORM", "Paquete SCORM"),
                        ],
                        default="EJERCICIO",
                        max_length=20,
                        verbose_name="Tipo de Material",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "scorm_package",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="portfolio_materials",
                        to="scorm_packager.scormpackage",
                        verbose_name="Paquete SCORM",
                    ),
                ),
                (
                    "topic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="materials",
                        to="portfolios.portfoliotopic",
                        verbose_name="Tema de Portafolio",
                    ),
                ),
            ],
            options={
                "verbose_name": "Material de Portafolio",
                "verbose_name_plural": "Materiales de Portafolio",
                "ordering": ["-created_at"],
            },
        ),
    ]
