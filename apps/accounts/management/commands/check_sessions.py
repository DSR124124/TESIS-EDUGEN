from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.conf import settings
from django.utils import timezone
import os

class Command(BaseCommand):
    help = 'Diagnosticar problemas de sesiones en Azure'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Diagnóstico de Sesiones EduGen'))
        self.stdout.write('=' * 50)
        
        # Configuración actual
        self.stdout.write(f"📋 ENGINE: {settings.SESSION_ENGINE}")
        self.stdout.write(f"📋 COOKIE_AGE: {settings.SESSION_COOKIE_AGE} segundos")
        self.stdout.write(f"📋 COOKIE_NAME: {getattr(settings, 'SESSION_COOKIE_NAME', 'sessionid')}")
        self.stdout.write(f"📋 COOKIE_SECURE: {getattr(settings, 'SESSION_COOKIE_SECURE', False)}")
        self.stdout.write(f"📋 COOKIE_HTTPONLY: {getattr(settings, 'SESSION_COOKIE_HTTPONLY', True)}")
        self.stdout.write(f"📋 COOKIE_SAMESITE: {getattr(settings, 'SESSION_COOKIE_SAMESITE', None)}")
        
        # Estado de la base de datos
        try:
            total_sessions = Session.objects.count()
            active_sessions = Session.objects.filter(expire_date__gt=timezone.now()).count()
            expired_sessions = total_sessions - active_sessions
            
            self.stdout.write(f"🗄️  Total sesiones: {total_sessions}")
            self.stdout.write(f"✅ Sesiones activas: {active_sessions}")
            self.stdout.write(f"⚠️  Sesiones expiradas: {expired_sessions}")
            
            # Mostrar últimas 5 sesiones
            if active_sessions > 0:
                self.stdout.write("\n🔍 Últimas 5 sesiones activas:")
                recent_sessions = Session.objects.filter(
                    expire_date__gt=timezone.now()
                ).order_by('-expire_date')[:5]
                
                for i, session in enumerate(recent_sessions, 1):
                    self.stdout.write(f"  {i}. Expira: {session.expire_date}")
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error accediendo a sesiones: {e}"))
        
        # Información del entorno
        self.stdout.write(f"\n🌐 WEBSITE_HOSTNAME: {os.environ.get('WEBSITE_HOSTNAME', 'No configurado')}")
        self.stdout.write(f"🌐 ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        self.stdout.write(f"🔒 CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])}")
        
        # Recomendaciones
        self.stdout.write(self.style.WARNING("\n💡 Recomendaciones:"))
        self.stdout.write("   1. Verificar que las cookies se están enviando")
        self.stdout.write("   2. Confirmar que HTTPS está activo")
        self.stdout.write("   3. Revisar configuración del navegador")
        self.stdout.write("   4. Limpiar cookies del navegador si es necesario")
        
        self.stdout.write(self.style.SUCCESS('\n✅ Diagnóstico completado')) 