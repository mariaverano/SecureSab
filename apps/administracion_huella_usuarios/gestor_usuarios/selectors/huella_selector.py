from apps.administracion_huella_usuarios.gestor_usuarios.models import Huella

def obtener_usuarios_con_estado_huella():
    """Obtiene todos los usuarios con su estado de huella"""
    from apps.login.models import Usuarios
    return Usuarios.objects.raw("""
        SELECT u.*, r.name as nombre_rol, h.tiene_huella, h.fecha_registro as fecha_huella
        FROM usuarios u
        LEFT JOIN role_user ru ON u.id_usuario = ru.id_usuario
        LEFT JOIN roles r ON ru.role_id = r.id
        LEFT JOIN huella h ON u.id_usuario = h.usuario_id
    """)

def obtener_huella_por_usuario(usuario):
    """Obtiene la huella de un usuario"""
    return Huella.objects.filter(usuario=usuario).first()