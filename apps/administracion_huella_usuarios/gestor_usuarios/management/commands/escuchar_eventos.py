# escuchar_eventos.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.login.models import Usuarios
from apps.reporte_monitoreo.coordinador.models import AsistenciaSede
import requests
from requests.auth import HTTPDigestAuth
import re
import time

class Command(BaseCommand):
    help = 'Escucha eventos del huellero en tiempo real'

    def handle(self, *args, **kwargs):
        ip_huellero = "192.168.1.13"
        usuario = "admin"
        password = "Dilan1105"
        
        self.stdout.write("🔌 Conectando al stream de eventos...")
        
        url = f'http://{ip_huellero}/ISAPI/Event/notification/alertStream'
        
        while True:
            try:
                response = requests.get(
                    url, 
                    auth=HTTPDigestAuth(usuario, password), 
                    stream=True,
                    timeout=30
                )
                
                self.stdout.write("✅ Conectado. Esperando eventos...")
                self.stdout.write("Presiona CTRL+C para salir")
                
                procesados = set()
                
                for line in response.iter_lines():
                    if line:
                        try:
                            texto = line.decode('utf-8')
                            
                            # Buscar número de serie del evento (evitar duplicados)
                            serial_match = re.search(r'"serialNo":\s*(\d+)', texto)
                            if serial_match:
                                serial = serial_match.group(1)
                                if serial in procesados:
                                    continue
                                procesados.add(serial)
                            
                            # Buscar cédula en el evento
                            match = re.search(r'"employeeNoString"\s*:\s*"(\d+)"', texto)
                            if match:
                                cedula = match.group(1)
                                if cedula:
                                    self.stdout.write(f"✅ Cédula detectada: {cedula}")
                                    
                                    try:
                                        usuario_obj = Usuarios.objects.get(cedula=cedula)
                                        ahora = timezone.now()
                                        hoy = ahora.date()
                                        hora_evento = ahora.time()
                                        
                                        # Buscar si ya tiene entrada hoy sin salida
                                        ultima_entrada_sin_salida = AsistenciaSede.objects.filter(
                                            id_usuario=usuario_obj,
                                            fecha=hoy,
                                            hora_salida__isnull=True
                                        ).last()
                                        
                                        if ultima_entrada_sin_salida:
                                            # Es una SALIDA
                                            ultima_entrada_sin_salida.hora_salida = hora_evento
                                            ultima_entrada_sin_salida.save()
                                            self.stdout.write(self.style.SUCCESS(
                                                f"   🔴 SALIDA: {usuario_obj.nombre} {usuario_obj.apellido} - {hora_evento}"
                                            ))
                                        else:
                                            # Es una ENTRADA
                                            AsistenciaSede.objects.create(
                                                id_usuario=usuario_obj,
                                                fecha=hoy,
                                                hora_entrada=hora_evento,
                                                estado_asistencia="presente"
                                            )
                                            self.stdout.write(self.style.SUCCESS(
                                                f"   🟢 ENTRADA: {usuario_obj.nombre} {usuario_obj.apellido} - {hora_evento}"
                                            ))
                                            
                                    except Usuarios.DoesNotExist:
                                        self.stdout.write(self.style.ERROR(f"   ❌ Usuario no existe: {cedula}"))
                                        
                        except Exception as e:
                            self.stdout.write(f"Error procesando línea: {e}")
                            
            except Exception as e:
                self.stdout.write(f"❌ Conexión perdida: {e}")
                self.stdout.write("🔄 Reintentando en 5 segundos...")
                time.sleep(5)