# management/commands/escuchar_huellas.py
from django.core.management.base import BaseCommand
import time
from apps.administracion_huella_usuarios.gestor_usuarios.services.hikvision_sdk import iniciar_sdk, sdk

class Command(BaseCommand):
    help = 'Escucha eventos del Hikvision usando SDK'

    def handle(self, *args, **kwargs):
        self.stdout.write("🔄 Iniciando SDK de Hikvision...")
        
        if not iniciar_sdk():
            self.stdout.write("❌ No se pudo conectar al huellero")
            return
        
        self.stdout.write("✅ Conectado. Esperando eventos...")
        
        # El SDK maneja los eventos automáticamente
        # Solo mantenemos el script corriendo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write("\n👋 Cerrando conexión...")
            sdk.cerrar()