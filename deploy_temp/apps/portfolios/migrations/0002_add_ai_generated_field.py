from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfoliomaterial',
            name='ai_generated',
            field=models.BooleanField(default=False, verbose_name='Generado por IA'),
        ),
    ] 