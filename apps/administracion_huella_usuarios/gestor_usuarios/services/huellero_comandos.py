# services/huellero_comandos.py
import requests
from requests.auth import HTTPDigestAuth

IP_HUELLERO = "192.168.1.13"
USER = "admin"
PASSWORD = "Dilan1105"

def iniciar_registro_huella_remoto(cedula):
    """Le dice al huellero: 'Preparate, voy a registrar la huella de esta persona'"""
    
    url = f"http://{IP_HUELLERO}/ISAPI/AccessControl/CaptureFingerPrint"
    
    # Versión 1: XML más simple (sin versión ni namespace)
    xml_data = f'''<CaptureFingerPrint>
        <employeeNo>{cedula}</employeeNo>
        <fingerNo>1</fingerNo>
        <repeatTime>2</repeatTime>
    </CaptureFingerPrint>'''
    
    response = requests.post(
        url,
        auth=HTTPDigestAuth(USER, PASSWORD),
        headers={"Content-Type": "application/xml"},
        data=xml_data,
        timeout=10
    )
    
    if response.status_code == 200:
        print(f"✅ Huellero en modo registro para cédula {cedula}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False