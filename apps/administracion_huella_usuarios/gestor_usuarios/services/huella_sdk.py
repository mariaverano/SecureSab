# services/huella_sdk.py
import ctypes
from ctypes import *
import os
from django.conf import settings

# Configuración del SDK (ajusta rutas según tu estructura)
SDK_LIB_PATH = os.path.join(settings.BASE_DIR, 'libs', 'HCNetSDK.dll')
IP_HUELLERO = "192.168.1.13"
PUERTO = 8000
USUARIO = "admin"
PASSWORD = "Dilan1105"

# Cargar el SDK
hcnetsdk = ctypes.CDLL(SDK_LIB_PATH)

def inicializar_sdk():
    """Inicializa el SDK de Hikvision"""
    hcnetsdk.NET_DVR_Init()
    print("✅ SDK inicializado")

def login_dispositivo():
    """Inicia sesión en el huellero"""
    # Estructura para datos de login
    class NET_DVR_USER_LOGIN_INFO(Structure):
        _fields_ = [
            ("sDeviceAddress", c_char * 129),
            ("byUseTransport", c_byte),
            ("wPort", c_ushort),
            ("sUserName", c_char * 64),
            ("sPassword", c_char * 64),
            ("cbLoginResult", c_void_p),
            ("pUser", c_void_p),
            ("bUseAsynLogin", c_bool),
            ("byProxyType", c_byte),
            ("byUseUTCTime", c_byte),
            ("byLoginMode", c_byte),
            ("byHttps", c_byte),
            ("iProxyID", c_int),
            ("byVerifyMode", c_byte),
            ("byRes2", c_byte * 119)
        ]
    
    login_info = NET_DVR_USER_LOGIN_INFO()
    login_info.sDeviceAddress = IP_HUELLERO.encode('utf-8')
    login_info.wPort = PUERTO
    login_info.sUserName = USUARIO.encode('utf-8')
    login_info.sPassword = PASSWORD.encode('utf-8')
    login_info.bUseAsynLogin = False
    
    # Llamar a NET_DVR_Login_V40
    lUserID = hcnetsdk.NET_DVR_Login_V40(byref(login_info), None)
    
    if lUserID < 0:
        error = hcnetsdk.NET_DVR_GetLastError()
        print(f"❌ Error de login: {error}")
        return None
    
    print(f"✅ Login exitoso. UserID: {lUserID}")
    return lUserID

def registrar_huella_sdk(usuario_id, lUserID):
    """
    Inicia el proceso de registro de huella en el dispositivo.
    NOTA: El usuario debe poner el dedo en el lector cuando el SDK lo solicite.
    """
    # Usar NET_DVR_StartRemoteConfig con comando NET_DVR_SET_FINGERPRINT_CFG_V50 (2184)
    # Esto es más complejo porque requiere manejar callbacks
    pass

def eliminar_huella_sdk(usuario_id, lUserID):
    """Elimina una huella del dispositivo usando NET_DVR_DEL_FINGERPRINT_CFG_V50 (2517)"""
    pass