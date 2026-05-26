from apps.login.models import Usuarios, Roles, RoleUser
from .actividad_service import registrar_actividad

def crear_usuario(request, datos):
    """Crea un nuevo usuario"""
    cedula = datos.get('cedula')
    nombre = datos.get('nombre')
    apellido = datos.get('apellido')
    correo = datos.get('correo')
    telefono = datos.get('telefono')
    password = datos.get('password', '123')
    rol_id = datos.get('rol_id')
    ficha_id = datos.get('ficha_id')
    
    # Obtener nombre del rol
    rol_nombre = 'sin rol'
    if rol_id:
        try:
            rol = Roles.objects.get(id=rol_id)
            rol_nombre = rol.name
        except Roles.DoesNotExist:
            rol_nombre = 'rol no encontrado'
    
    # Crear usuario
    usuario = Usuarios.objects.create_user(
        cedula=cedula,
        password=password,
        nombre=nombre,
        apellido=apellido,
        correo=correo,
        telefono=telefono,
        is_active=True,
        is_staff=(rol_nombre == 'gestor')
    )
    
    if rol_id:
        RoleUser.objects.create(id_usuario=usuario, role_id=rol_id)
    
    if ficha_id:
        usuario.id_ficha_id = ficha_id
        usuario.save()
    
    # Registrar actividad
    registrar_actividad(
        usuario=request.user,
        tipo_accion='CREATE',
        actividad='Creación de usuario',
        descripcion=f'Se creó el usuario {nombre} {apellido} con cédula {cedula} y rol {rol_nombre}',
        request=request
    )
    
    return usuario

def actualizar_usuario(usuario, datos):
    """Actualiza un usuario existente"""
    usuario.nombre = datos.get('nombre', usuario.nombre)
    usuario.apellido = datos.get('apellido', usuario.apellido)
    usuario.correo = datos.get('correo', usuario.correo)
    usuario.telefono = datos.get('telefono', usuario.telefono)
    usuario.save()
    
    rol_id = datos.get('rol_id')
    if rol_id:
        RoleUser.objects.update_or_create(
            id_usuario=usuario,
            defaults={'role_id': rol_id}
        )
    
    return usuario

def eliminar_usuario(request, usuario):
    """Elimina un usuario"""
    nombre = f"{usuario.nombre} {usuario.apellido}"
    cedula = usuario.cedula
    
    registrar_actividad(
        usuario=request.user,
        tipo_accion='DELETE',
        actividad='Eliminación de usuario',
        descripcion=f'Se eliminó al usuario {nombre} con cédula {cedula}',
        request=request
    )
    
    usuario.delete()

def cambiar_estado_usuario(request, usuario, accion):
    """Activa o desactiva un usuario"""
    if accion == 'desactivar':
        usuario.estado = 'Inactivo'
        usuario.is_active = False
        tipo_accion = 'DESACTIVAR'
        actividad = 'Desactivación de usuario'
        descripcion = f'Se desactivó al usuario {usuario.nombre} {usuario.apellido} (cédula: {usuario.cedula})'
    else:
        usuario.estado = 'Activo'
        usuario.is_active = True
        tipo_accion = 'ACTIVAR'
        actividad = 'Activación de usuario'
        descripcion = f'Se activó al usuario {usuario.nombre} {usuario.apellido} (cédula: {usuario.cedula})'
    
    usuario.save()
    
    registrar_actividad(
        usuario=request.user,
        tipo_accion=tipo_accion,
        actividad=actividad,
        descripcion=descripcion,
        request=request
    )

def procesar_carga_masiva(request, csv_file, password_default):
    """
    Procesa la carga masiva de usuarios desde un archivo CSV
    
    Returns:
        tuple: (creados, errores, errores_lista)
    """
    import csv
    from apps.login.models import Usuarios, Roles
    from apps.reporte_monitoreo.coordinador.models import Ficha
    
    content = csv_file.read().decode('utf-8')
    if content.startswith('\ufeff'):
        content = content[1:]
    
    lines = content.splitlines()
    reader = csv.DictReader(lines)
    
    creados = 0
    errores = 0
    errores_lista = []
    
    for index, row in enumerate(reader, start=2):
        cedula = row.get('cedula', '').strip()
        nombre = row.get('nombre', '').strip()
        apellido = row.get('apellido', '').strip()
        correo = row.get('correo', '').strip()
        telefono = row.get('telefono', '').strip()
        rol_nombre = row.get('rol', '').strip().lower()
        ficha_numero = row.get('ficha', '').strip()
        
        # Validar campos obligatorios
        if not cedula or not nombre or not apellido or not correo or not telefono or not rol_nombre:
            errores += 1
            errores_lista.append(f'Fila {index}: Faltan campos obligatorios')
            continue
        
        # Validar cédula única
        if Usuarios.objects.filter(cedula=cedula).exists():
            errores += 1
            errores_lista.append(f'Cédula {cedula} ya existe')
            continue
        
        # Validar rol
        try:
            rol = Roles.objects.get(name=rol_nombre)
        except Roles.DoesNotExist:
            errores += 1
            errores_lista.append(f'Rol {rol_nombre} no existe')
            continue
        
        # Crear usuario
        usuario = Usuarios.objects.create_user(
            cedula=cedula,
            password=password_default,
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            telefono=telefono,
            is_active=True,
            is_staff=(rol_nombre == 'gestor')
        )
        
        RoleUser.objects.create(id_usuario=usuario, role=rol)
        
        # Asignar ficha si es aprendiz
        if rol_nombre == 'aprendiz' and ficha_numero:
            ficha = Ficha.objects.filter(numero_ficha=ficha_numero).first()
            if ficha:
                usuario.id_ficha = ficha
                usuario.save()
        
        creados += 1
    
    return creados, errores, errores_lista