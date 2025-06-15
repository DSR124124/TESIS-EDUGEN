from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.portfolios.models import PortfolioMaterial

try:
    from colorama import Fore, Style, init
    # Inicializar colorama
    init(autoreset=True)
except ImportError:
    # Fallback si colorama no está disponible
    class Fore:
        CYAN = BLUE = GREEN = YELLOW = ""
    class Style:
        RESET_ALL = ""



class Command(BaseCommand):
    help = 'Verifica y reporta la clasificación de materiales (clase vs personalizado)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix', 
            action='store_true', 
            help='Aplicar correcciones automáticas a materiales mal clasificados'
        )
        parser.add_argument(
            '--verbose', 
            action='store_true', 
            help='Mostrar información detallada'
        )
        parser.add_argument(
            '--topic-id', 
            type=int, 
            help='Solo verificar materiales de un tema específico'
        )

    def handle(self, *args, **options):
        self.stdout.write(f"\n{Fore.CYAN}=== VERIFICACIÓN DE CLASIFICACIÓN DE MATERIALES ==={Style.RESET_ALL}\n")
        
        # Filtrar por tema si se especifica
        if options['topic_id']:
            materials = PortfolioMaterial.objects.filter(topic_id=options['topic_id'])
            self.stdout.write(f"📍 Verificando solo materiales del tema ID: {options['topic_id']}")
        else:
            materials = PortfolioMaterial.objects.all()
            
        total_materials = materials.count()
        self.stdout.write(f"📊 Total de materiales a verificar: {total_materials}")
        
        # Contadores
        class_materials = 0
        personal_materials = 0
        ai_class_materials = 0
        ai_personal_materials = 0
        needs_fixing = []
        
        for material in materials:
            ai_generated = getattr(material, 'ai_generated', False)
            is_class_material = getattr(material, 'is_class_material', False)
            
            if options['verbose']:
                status = "✅" if (ai_generated or is_class_material) else "⚠️"
                self.stdout.write(
                    f"{status} ID:{material.id} - {material.title[:50]}... | "
                    f"AI: {'Sí' if ai_generated else 'No'} | "
                    f"Clase: {'Sí' if is_class_material else 'No'}"
                )
            
            # Clasificar y contar
            if ai_generated and is_class_material:
                ai_class_materials += 1
            elif ai_generated and not is_class_material:
                ai_personal_materials += 1
            elif not ai_generated and is_class_material:
                class_materials += 1
            else:
                personal_materials += 1
                
            # Detectar materiales que podrían necesitar corrección
            # Materiales AI sin clasificación clara
            if ai_generated and not hasattr(material, 'is_class_material'):
                needs_fixing.append({
                    'material': material,
                    'issue': 'Material AI sin campo is_class_material definido',
                    'suggested_fix': 'Establecer is_class_material=False (personalizado por defecto)'
                })
        
        # Mostrar resumen
        self.stdout.write(f"\n{Fore.GREEN}=== RESUMEN DE CLASIFICACIÓN ==={Style.RESET_ALL}")
        self.stdout.write(f"📚 {Fore.BLUE}Materiales de Clase (No-AI):{Style.RESET_ALL} {class_materials}")
        self.stdout.write(f"🤖 {Fore.BLUE}Materiales de Clase (AI):{Style.RESET_ALL} {ai_class_materials}")
        self.stdout.write(f"👤 {Fore.GREEN}Materiales Personalizados (No-AI):{Style.RESET_ALL} {personal_materials}")
        self.stdout.write(f"🧠 {Fore.GREEN}Materiales Personalizados (AI):{Style.RESET_ALL} {ai_personal_materials}")
        
        total_class = class_materials + ai_class_materials
        total_personal = personal_materials + ai_personal_materials
        
        self.stdout.write(f"\n{Fore.CYAN}TOTALES:{Style.RESET_ALL}")
        self.stdout.write(f"🏫 Total Material de Clase: {total_class}")
        self.stdout.write(f"👨‍🎓 Total Material Personalizado: {total_personal}")
        
        # Mostrar materiales que necesitan corrección
        if needs_fixing:
            self.stdout.write(f"\n{Fore.YELLOW}=== MATERIALES QUE NECESITAN ATENCIÓN ==={Style.RESET_ALL}")
            for item in needs_fixing:
                self.stdout.write(f"⚠️  ID:{item['material'].id} - {item['material'].title}")
                self.stdout.write(f"   Problema: {item['issue']}")
                self.stdout.write(f"   Solución sugerida: {item['suggested_fix']}")
                
            if options['fix']:
                self.stdout.write(f"\n{Fore.CYAN}Aplicando correcciones...{Style.RESET_ALL}")
                fixed_count = 0
                for item in needs_fixing:
                    material = item['material']
                    if 'is_class_material=False' in item['suggested_fix']:
                        material.is_class_material = False
                        material.save()
                        fixed_count += 1
                        self.stdout.write(f"✅ Corregido: {material.title}")
                
                self.stdout.write(f"\n{Fore.GREEN}✅ Se corrigieron {fixed_count} materiales{Style.RESET_ALL}")
            else:
                self.stdout.write(f"\n{Fore.YELLOW}💡 Usa --fix para aplicar las correcciones automáticamente{Style.RESET_ALL}")
        else:
            self.stdout.write(f"\n{Fore.GREEN}✅ Todos los materiales están correctamente clasificados{Style.RESET_ALL}")
        
        # Verificar materiales AI generados
        self.stdout.write(f"\n{Fore.CYAN}=== VERIFICACIÓN DE MATERIALES AI ==={Style.RESET_ALL}")
        ai_materials_total = materials.filter(ai_generated=True).count()
        self.stdout.write(f"🤖 Total de materiales AI generados: {ai_materials_total}")
        
        if ai_materials_total > 0:
            self.stdout.write(f"✅ Se encontraron materiales generados con IA")
        else:
            self.stdout.write(f"⚠️  No se encontraron materiales generados con IA")
        
        self.stdout.write(f"\n{Fore.GREEN}=== VERIFICACIÓN COMPLETADA ==={Style.RESET_ALL}") 