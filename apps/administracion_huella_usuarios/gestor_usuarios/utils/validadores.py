import re

def validar_cedula(cedula):
    """Valida que la cédula contenga solo números"""
    return cedula and cedula.isdigit()

def validar_email(email):
    """Valida el formato del email"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_telefono(telefono):
    """Valida que el teléfono contenga solo números"""
    return telefono.isdigit() if telefono else True

def filtrar_usuarios_por_busqueda(usuarios, buscar):
    """Filtra usuarios por búsqueda"""
    if not buscar:
        return usuarios
    
    return [u for u in usuarios if 
            buscar.lower() in (u.nombre or '').lower() or 
            buscar.lower() in (u.apellido or '').lower() or 
            buscar.lower() in (u.cedula or '').lower() or
            buscar.lower() in (u.correo or '').lower()]

def filtrar_usuarios_por_rol(usuarios, rol):
    """Filtra usuarios por rol"""
    if not rol:
        return usuarios
    return [u for u in usuarios if getattr(u, 'nombre_rol', '') == rol]

def filtrar_usuarios_por_estado(usuarios, estado):
    """Filtra usuarios por estado"""
    if not estado:
        return usuarios
    return [u for u in usuarios if u.estado == estado]