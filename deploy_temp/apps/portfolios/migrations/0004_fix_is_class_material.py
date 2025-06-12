# Generated migration to fix is_class_material field

from django.db import migrations

def fix_is_class_material(apps, schema_editor):
    PortfolioMaterial = apps.get_model('portfolios', 'PortfolioMaterial')
    
    # Establecer is_class_material=True para todos los materiales existentes que tienen None/NULL
    materials_to_update = PortfolioMaterial.objects.filter(is_class_material__isnull=True)
    count = materials_to_update.count()
    print(f"Actualizando {count} materiales con is_class_material=NULL")
    
    materials_to_update.update(is_class_material=True)
    print(f"Se actualizaron {count} materiales a is_class_material=True")

def reverse_fix_is_class_material(apps, schema_editor):
    # No podemos revertir de manera segura
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0003_portfoliomaterial_is_class_material'),
    ]

    operations = [
        migrations.RunPython(fix_is_class_material, reverse_fix_is_class_material),
    ] 