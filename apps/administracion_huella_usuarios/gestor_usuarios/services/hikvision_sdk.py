# services/hikvision_sdk.py
import ctypes
from ctypes import *
import os
from django.conf import settings
import time

# ============================================
# CONFIGURACIÓN
# ============================================
LIBS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'libs')
os.add_dll_directory(LIBS_DIR)

# Cargar el SDK
HCNetSDK = ctypes.CDLL(os.path.join(LIBS_DIR, 'HCNetSDK.dll'))

IP_HUELLERO = "192.168.1.13"
PUERTO = 80
USUARIO = "admin"
PASSWORD = "Dilan1105"

# ============================================
# CONSTANTES DEL SDK
# ============================================
NET_DVR_SET_FINGERPRINT_CFG_V50 = 2184  # Para registrar huella
NET_DVR_GET_FINGERPRINT_CFG_V50 = 2183  # Para consultar huella
NET_DVR_DEL_FINGERPRINT_CFG_V50 = 2517  # Para eliminar huella

# Estados de callback
NET_SDK_CALLBACK_TYPE_STATUS = 0
NET_SDK_CALLBACK_STATUS_SUCCESS = 1000

# ============================================
# ESTRUCTURAS DE DATOS
# ============================================

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

class NET_DVR_FINGER_PRINT_INFO_COND_V50(Structure):
    _fields_ = [
        ("dwSize", c_uint),
        ("byEmployeeNo", c_char * 32),
        ("byRes", c_char * 32)
    ]

class NET_DVR_FINGER_PRINT_CFG_V50(Structure):
    _fields_ = [
        ("dwSize", c_uint),
        ("byEmployeeNo", c_char * 32),
        ("byCardNo", c_char * 32),
        ("dwFingerPrintLen", c_uint),
        ("byEnableCardReader", c_byte * 512),
        ("byFingerPrintID", c_byte),
        ("byFingerType", c_byte),
        ("byRes1", c_byte * 30),
        ("byFingerData", c_byte * 3072),
        ("byLeaderFP", c_byte * 256),
        ("byRes", c_byte * 128)
    ]

# ============================================
# VARIABLES GLOBALES
# ============================================
lUserID = -1
callback_registro = None

# ============================================
# CALLBACK PARA RECIBIR CONFIRMACIÓN
# ============================================

CALLBACK_TYPE = CFUNCTYPE(None, c_uint, c_void_p, c_uint, c_void_p)

def proceso_callback(dwType, lpBuffer, dwBufLen, pUserData):
    """Callback que recibe la confirmación del huellero"""
    print(f"📞 Callback recibido - Tipo: {dwType}")
    
    if dwType == NET_SDK_CALLBACK_TYPE_STATUS and lpBuffer:
        status = c_uint.from_address(lpBuffer).value
        print(f"   Estado: {status}")
        
        if status == NET_SDK_CALLBACK_STATUS_SUCCESS:
            print("✅ ¡Huella registrada exitosamente!")
            return 1000  # Éxito
    
    return 0

# ============================================
# FUNCIONES PRINCIPALES
# ============================================

def inicializar_sdk():
    """Inicializa el SDK de Hikvision"""
    print("🔧 Inicializando SDK...")
    HCNetSDK.NET_DVR_Init()
    HCNetSDK.NET_DVR_SetConnectTime(2000, 1)
    print("✅ SDK inicializado")
    return True


# services/hikvision_sdk.py (actualizado)

def conectar_huellero():
    """Conecta al huellero usando el método más simple"""
    global lUserID
    
    print(f"🔌 Conectando a {IP_HUELLERO}:{PUERTO}...")
    
    # Usar la función más simple de login (NET_DVR_Login_V30)
    # Esta es más compatible con modelos Value Series
    
    # Configurar la estructura simplificada
    class NET_DVR_DEVICEINFO_V30(Structure):
        _fields_ = [
            ("sSerialNumber", c_char * 48),
            ("byAlarmInPortNum", c_byte),
            ("byAlarmOutPortNum", c_byte),
            ("byDiskNum", c_byte),
            ("byDVRType", c_byte),
            ("byChanNum", c_byte),
            ("byStartChan", c_byte),
            ("byAudioChanNum", c_byte),
            ("byIPChanNum", c_byte),
            ("byZeroChanNum", c_byte),
            ("byMainProto", c_byte),
            ("bySubProto", c_byte),
            ("bySupport", c_byte),
            ("bySupport1", c_byte),
            ("bySupport2", c_byte),
            ("wDevType", c_ushort),
            ("byRes2", c_byte * 2),
            ("byAnalogChanNum", c_byte),
            ("byStartDTalkChan", c_byte),
            ("byStartDTalkChan1", c_byte),
            ("bySupportIPChan", c_byte),
            ("bySupportIPDocChan", c_byte),
            ("byRes3", c_byte * 8)
        ]
    
    device_info = NET_DVR_DEVICEINFO_V30()
    
    # Llamar a NET_DVR_Login_V30 (más simple que V40)
    login_func = HCNetSDK.NET_DVR_Login_V30
    login_func.argtypes = [c_char_p, c_ushort, c_char_p, c_char_p, POINTER(NET_DVR_DEVICEINFO_V30)]
    login_func.restype = c_int
    
    lUserID = login_func(
        IP_HUELLERO.encode('utf-8'),
        PUERTO,
        USUARIO.encode('utf-8'),
        PASSWORD.encode('utf-8'),
        byref(device_info)
    )
    
    if lUserID < 0:
        error = HCNetSDK.NET_DVR_GetLastError()
        print(f"❌ Error de conexión: {error}")
        return None
    
    print(f"✅ Conectado. UserID: {lUserID}")
    print(f"   Dispositivo: {device_info.sSerialNumber.decode('utf-8')}")
    return lUserID



def iniciar_registro_huella_sdk(cedula, nombre=""):
    """Inicia el proceso de registro de huella usando el SDK"""
    global callback_registro
    
    if lUserID < 0:
        print("❌ No hay conexión activa")
        return False
    
    print(f"🖐️ Iniciando registro de huella para cédula {cedula}")
    
    # 1. Preparar la condición
    cond = NET_DVR_FINGER_PRINT_INFO_COND_V50()
    cond.dwSize = sizeof(NET_DVR_FINGER_PRINT_INFO_COND_V50)
    cond.byEmployeeNo = str(cedula).encode('utf-8')
    
    # 2. Configurar el callback
    callback_registro = CALLBACK_TYPE(proceso_callback)
    
    # 3. Iniciar configuración remota
    hHandle = HCNetSDK.NET_DVR_StartRemoteConfig(
        lUserID,
        NET_DVR_SET_FINGERPRINT_CFG_V50,
        byref(cond),
        sizeof(cond),
        callback_registro,
        None
    )
    
    if hHandle < 0:
        print(f"❌ Error al iniciar configuración remota: {HCNetSDK.NET_DVR_GetLastError()}")
        return False
    
    print(f"✅ Configuración remota iniciada. Handle: {hHandle}")
    print("📌 El usuario debe poner su dedo en el escáner del huellero...")
    
    return True

def cerrar_conexion():
    """Cierra la conexión y limpia el SDK"""
    if lUserID >= 0:
        HCNetSDK.NET_DVR_Logout(lUserID)
    HCNetSDK.NET_DVR_Cleanup()
    print("👋 SDK cerrado")