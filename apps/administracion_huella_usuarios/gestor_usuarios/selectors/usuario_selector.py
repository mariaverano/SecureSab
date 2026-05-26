from apps.login.models import Usuarios, Roles, RoleUser
from apps.reporte_monitoreo.coordinador.models import Ficha, Jornada

def obtener_todos_usuarios_con_roles():
    """Obtiene todos los usuarios con su rol"""
    query = """
        SELECT u.*, r.name as nombre_rol
        FROM usuarios u
        LEFT JOIN role_user ru ON u.id_usuario = ru.id_usuario
        LEFT JOIN roles r ON ru.role_id = r.id
    """
    return Usuarios.objects.raw(query)

def obtener_usuario_por_id(id_usuario):
    """Obtiene un usuario por su ID"""
    return Usuarios.objects.filter(id_usuario=id_usuario).first()

def obtener_usuario_por_cedula(cedula):
    """Obtiene un usuario por su cédula"""
    return Usuarios.objects.filter(cedula=cedula).first()

def existe_usuario_por_cedula(cedula):
    """Verifica si existe un usuario con esa cédula"""
    return Usuarios.objects.filter(cedula=cedula).exists()

def obtener_todos_roles():
    """Obtiene todos los roles disponibles"""
    return Roles.objects.all()

def obtener_fichas_activas():
    """Obtiene todas las fichas activas"""
    return Ficha.objects.filter(estado='Activa')

def obtener_todas_jornadas():
    """Obtiene todas las jornadas"""
    return Jornada.objects.all()