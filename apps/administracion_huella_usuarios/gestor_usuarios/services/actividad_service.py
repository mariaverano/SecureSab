from apps.administracion_huella_usuarios.gestor_usuarios.models import registro_actividad
from django.utils import timezone

def registrar_actividad(usuario, tipo_accion, actividad, descripcion="", request=None):
    """Registra una actividad en la bitácora"""
    try:
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        registro_actividad.objects.create(
            id_usuario=usuario,
            tipo_accion=tipo_accion,
            actividad=actividad,
            descripcion=descripcion,
            ip_address=ip_address,
            user_agent=user_agent,
            fecha=timezone.now().date(),
            hora=timezone.now().time()
        )
    except Exception as e:
        print(f"Error al registrar actividad: {e}")