# hikvision_service.py
from datetime import datetime
import requests
from requests.auth import HTTPDigestAuth
from django.core.cache import cache
from apps.login.models import Usuarios

IP = "192.168.1.13"
USER = "admin"
PASSWORD = "Dilan1105"

# Mapeo de IDs del huellero a cédulas reales
MAPEO_CEDULAS = {
    '1': '1000856944',
}

# Fecha desde la cual consultar eventos (ajústala según tus necesidades)
FECHA_INICIO = "2026-01-01T00:00:00Z"

def obtener_eventos():
    """Consulta eventos desde una fecha fija"""
    
    url = f"http://{IP}/ISAPI/AccessControl/AcsEvent?format=json"
    
    payload = {
        "AcsEventCond": {
            "searchID": "1",
            "searchResultPosition": 0,
            "maxResults": 50,  # Traer más eventos
            "startTime": FECHA_INICIO,
            "endTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            auth=HTTPDigestAuth(USER, PASSWORD),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error de conexión: {e}")
        return {}

def procesar_eventos():
    """Procesa eventos nuevos (no repetidos)"""
    data = obtener_eventos()
    
    if "AcsEvent" not in data:
        print("No hay datos de eventos")
        return
    
    eventos = data["AcsEvent"].get("InfoList", [])
    
    if not eventos:
        print("No hay eventos en el rango de fechas")
        return
    
    print(f"📌 Procesando {len(eventos)} evento(s)...")
    
    for evento in eventos:
        cedula_huellero = evento.get("employeeNoString")
        fecha_hora = evento.get("time")
        
        if not cedula_huellero:
            continue
        
        # Crear una clave única para este evento (evitar duplicados)
        clave_evento = f"evento_{cedula_huellero}_{fecha_hora}"
        
        # Si ya procesamos este evento, lo saltamos
        if cache.get(clave_evento):
            continue
        
        # Marcar como procesado (expira en 1 hora)
        cache.set(clave_evento, True, 3600)
        
        # Aplicar mapeo de cédula
        cedula_bd = MAPEO_CEDULAS.get(cedula_huellero, cedula_huellero)
        
        print(f"   ID huellero: '{cedula_huellero}' → Cédula BD: '{cedula_bd}' - Hora: {fecha_hora}")
        
        try:
            usuario = Usuarios.objects.get(cedula=cedula_bd)
            print(f"   ✅ {usuario.nombre} {usuario.apellido}")
            
            # Aquí guardas la asistencia...
            
        except Usuarios.DoesNotExist:
            print(f"   ❌ Usuario no existe con cédula: '{cedula_bd}'")