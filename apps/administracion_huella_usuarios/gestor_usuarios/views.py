from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Usuarios

from .selectors import (
    obtener_todos_usuarios_con_roles,
    obtener_usuario_por_id,
    existe_usuario_por_cedula,
    obtener_todos_roles,
    obtener_fichas_activas,
    obtener_todas_jornadas,
    obtener_usuarios_con_estado_huella,
    obtener_todas_actividades,
)

from .services.usuario_service import procesar_carga_masiva

from .services import (
    crear_usuario,
    actualizar_usuario,
    eliminar_usuario,
    cambiar_estado_usuario,
    registrar_huella,
    eliminar_huella,
    registrar_actividad,
)
from .utils.validadores import (
    filtrar_usuarios_por_busqueda,
    filtrar_usuarios_por_rol,
    filtrar_usuarios_por_estado,
)
from .selectors.actividad_selector import filtrar_actividades


# ==================== GESTIÓN DE USUARIOS ====================

@login_required
def gestionar_usuarios(request):
    """Vista principal con filtros y tabla de usuarios"""
    
    usuarios = obtener_todos_usuarios_con_roles()
    
    buscar = request.GET.get('buscar', '')
    rol_filtro = request.GET.get('rol', '')
    estado_filtro = request.GET.get('estado', '')
    
    usuarios_lista = list(usuarios)
    usuarios_lista = filtrar_usuarios_por_busqueda(usuarios_lista, buscar)
    usuarios_lista = filtrar_usuarios_por_rol(usuarios_lista, rol_filtro)
    usuarios_lista = filtrar_usuarios_por_estado(usuarios_lista, estado_filtro)
    
    context = {
        'usuarios': usuarios_lista,
        'roles': obtener_todos_roles(),
        'fichas': obtener_fichas_activas(),
        'jornadas': obtener_todas_jornadas(),
        'filtros': {
            'buscar': buscar,
            'rol': rol_filtro,
            'estado': estado_filtro,
        }
    }
    return render(request, 'gestionar_usuarios.html', context)


@login_required
def crear_usuario_view(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        
        if existe_usuario_por_cedula(cedula):
            messages.error(request, f'Ya existe un usuario con la cédula {cedula}')
            return redirect('gestor_usuarios:gestionar_usuarios')
        
        datos = {
            'cedula': cedula,
            'nombre': request.POST.get('nombre'),
            'apellido': request.POST.get('apellido'),
            'correo': request.POST.get('correo'),
            'telefono': request.POST.get('telefono'),
            'password': request.POST.get('password'),
            'rol_id': request.POST.get('rol'),
            'ficha_id': request.POST.get('ficha'),
        }
        
        usuario = crear_usuario(request, datos)
        messages.success(request, f'Usuario {usuario.nombre} {usuario.apellido} creado exitosamente')
        return redirect('gestor_usuarios:gestionar_usuarios')
    
    return redirect('gestor_usuarios:gestionar_usuarios')


@login_required
def editar_usuario_view(request, id_usuario):
    usuario = get_object_or_404(Usuarios, id_usuario=id_usuario)
    
    if request.method == 'POST':
        datos = {
            'nombre': request.POST.get('nombre'),
            'apellido': request.POST.get('apellido'),
            'correo': request.POST.get('correo'),
            'telefono': request.POST.get('telefono'),
            'rol_id': request.POST.get('rol'),
        }
        
        actualizar_usuario(usuario, datos)
        
        registrar_actividad(
            usuario=request.user,
            tipo_accion='UPDATE',
            actividad='Edición de usuario',
            descripcion=f'Se editó el usuario {usuario.nombre} {usuario.apellido}',
            request=request
        )
        
        messages.success(request, 'Usuario actualizado correctamente')
        return redirect('gestor_usuarios:gestionar_usuarios')
    
    return redirect('gestor_usuarios:gestionar_usuarios')


@login_required
def eliminar_usuario_view(request, id_usuario):
    usuario = get_object_or_404(Usuarios, id_usuario=id_usuario)
    
    if request.method == 'POST':
        eliminar_usuario(request, usuario)
        messages.success(request, f'Usuario eliminado permanentemente')
    
    return redirect('gestor_usuarios:gestionar_usuarios')


@login_required
def cambiar_estado_usuario_view(request, id_usuario):
    usuario = get_object_or_404(Usuarios, id_usuario=id_usuario)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        cambiar_estado_usuario(request, usuario, accion)
        
        if accion == 'desactivar':
            messages.warning(request, f'Usuario {usuario.nombre} {usuario.apellido} desactivado')
        else:
            messages.success(request, f'Usuario {usuario.nombre} {usuario.apellido} activado')
    
    return redirect('gestor_usuarios:gestionar_usuarios')


# ==================== HUELLAS ====================

@login_required
def gestion_huellas(request):
    usuarios = obtener_usuarios_con_estado_huella()
    
    buscar = request.GET.get('buscar', '')
    estado_huella = request.GET.get('estado_huella', '')
    rol_filtro = request.GET.get('rol', '')
    
    usuarios_lista = list(usuarios)
    
    if buscar:
        usuarios_lista = [u for u in usuarios_lista if 
                   buscar.lower() in (u.nombre or '').lower() or 
                   buscar.lower() in (u.apellido or '').lower() or 
                   buscar.lower() in (u.cedula or '').lower()]
    
    if estado_huella == 'con_huella':
        usuarios_lista = [u for u in usuarios_lista if getattr(u, 'tiene_huella', False) == True]
    elif estado_huella == 'sin_huella':
        usuarios_lista = [u for u in usuarios_lista if getattr(u, 'tiene_huella', False) != True]
    
    if rol_filtro:
        usuarios_lista = [u for u in usuarios_lista if getattr(u, 'nombre_rol', '') == rol_filtro]
    
    context = {
        'usuarios': usuarios_lista,
        'roles': obtener_todos_roles(),
        'filtros': {
            'buscar': buscar,
            'estado_huella': estado_huella,
            'rol': rol_filtro,
        }
    }
    return render(request, 'gestion_huellas.html', context)


# views.py



    

@login_required
def eliminar_huella_usuario_view(request, id_usuario):
    usuario = get_object_or_404(Usuarios, id_usuario=id_usuario)
    
    if eliminar_huella(request, usuario):
        messages.success(request, f'✅ Huella eliminada para {usuario.nombre} {usuario.apellido}')
    else:
        messages.warning(request, 'El usuario no tiene huella registrada')
    
    return redirect('gestor_usuarios:gestion_huellas')


# ==================== BITÁCORA ====================

@login_required
def registro_actividad_view(request):
    actividades = obtener_todas_actividades()
    
    buscar = request.GET.get('buscar', '')
    tipo_accion = request.GET.get('tipo_accion', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    actividades = filtrar_actividades(actividades, buscar, tipo_accion, fecha_desde, fecha_hasta)
    
    paginator = Paginator(actividades, 20)
    page = request.GET.get('page', 1)
    actividades_paginadas = paginator.get_page(page)
    
    context = {
        'actividades': actividades_paginadas,
        'filtros': {
            'buscar': buscar,
            'tipo_accion': tipo_accion,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    return render(request, 'registro_actividad.html', context)


# ==================== HISTORIAL DE FALLOS ====================

from .models import HistorialFallos
from django.db.models import Q

@login_required
def historial_fallos(request):
    fallos = HistorialFallos.objects.select_related('usuario').all()
    
    total_fallos = fallos.count()
    fallos_huella = fallos.filter(tipo_fallo='HUELLA_FALLIDA').count()
    fallos_sin_huella = fallos.filter(tipo_fallo='SIN_HUELLA').count()
    fallos_no_existe = fallos.filter(tipo_fallo='USUARIO_NO_EXISTE').count()
    
    buscar = request.GET.get('buscar', '')
    tipo_fallo = request.GET.get('tipo_fallo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    if buscar:
        fallos = fallos.filter(
            Q(cedula_intentada__icontains=buscar) |
            Q(usuario__nombre__icontains=buscar) |
            Q(usuario__apellido__icontains=buscar) |
            Q(usuario__cedula__icontains=buscar)
        )
    
    if tipo_fallo:
        fallos = fallos.filter(tipo_fallo=tipo_fallo)
    
    if fecha_desde:
        fallos = fallos.filter(fecha__gte=fecha_desde)
    
    if fecha_hasta:
        fallos = fallos.filter(fecha__lte=fecha_hasta)
    
    paginator = Paginator(fallos, 20)
    page = request.GET.get('page', 1)
    fallos_paginados = paginator.get_page(page)
    
    context = {
        'fallos': fallos_paginados,
        'total_fallos': total_fallos,
        'fallos_huella': fallos_huella,
        'fallos_sin_huella': fallos_sin_huella,
        'fallos_no_existe': fallos_no_existe,
        'filtros': {
            'buscar': buscar,
            'tipo_fallo': tipo_fallo,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    return render(request, 'historial_fallos.html', context)


# ==================== CARGA MASIVA ====================

@login_required
def carga_masiva_usuarios(request):
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        csv_file = request.FILES['archivo_csv']
        password_default = request.POST.get('password_default', '123')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'El archivo debe ser CSV')
            return redirect('gestor_usuarios:gestionar_usuarios')
        
        # Llamar al service
        creados, errores, errores_lista = procesar_carga_masiva(request, csv_file, password_default)
        
        # Registrar actividad
        registrar_actividad(
            usuario=request.user,
            tipo_accion='CARGA_MASIVA',
            actividad='Carga masiva de usuarios',
            descripcion=f'Se crearon {creados} usuarios mediante archivo CSV. Errores: {errores}',
            request=request
        )
        
        if creados > 0:
            messages.success(request, f'✅ Se crearon {creados} usuarios')
        if errores > 0:
            messages.warning(request, f'⚠️ {errores} errores')
        
        return redirect('gestor_usuarios:gestionar_usuarios')
    
    return redirect('gestor_usuarios:gestionar_usuarios')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

# Importa el modelo correcto desde autenticacion
from apps.login.models import Usuarios
@csrf_exempt
@require_http_methods(["POST"])
def webhook_huella(request):
    try:
        body = request.body.decode('utf-8')
        print(f"📦 Recibido: {body[:200]}")
        
        import re
        from django.utils import timezone
        from apps.login.models import Usuarios
        from apps.administracion_huella_usuarios.gestor_usuarios.models import AsistenciaSede
        
        match = re.search(r'"employeeNoString"\s*:\s*"(\d+)"', body)
        
        if match:
            cedula = match.group(1)
            print(f"✅ Cédula detectada: {cedula}")
            
            try:
                usuario = Usuarios.objects.get(cedula=cedula)
                ahora = timezone.now()
                hoy = ahora.date()
                
                # Verificar si ya tiene entrada hoy
                asistencia_hoy = AsistenciaSede.objects.filter(
                    id_usuario=usuario,
                    fecha=hoy
                ).first()
                
                if not asistencia_hoy:
                    # Primera marcación del día = ENTRADA
                    AsistenciaSede.objects.create(
                        id_usuario=usuario,
                        fecha=hoy,
                        hora_entrada=ahora.time(),
                        estado_asistencia="presente"
                    )
                    print(f"   🟢 ENTRADA: {usuario.nombre} {usuario.apellido} - {ahora.time()}")
                else:
                    # Segunda marcación = SALIDA (solo si no tiene hora_salida)
                    if not asistencia_hoy.hora_salida:
                        asistencia_hoy.hora_salida = ahora.time()
                        asistencia_hoy.save()
                        print(f"   🔴 SALIDA: {usuario.nombre} {usuario.apellido} - {ahora.time()}")
                    else:
                        print(f"   ⚠️ Ya tiene entrada y salida hoy")
                        
            except Usuarios.DoesNotExist:
                print(f"   ❌ Usuario no existe: {cedula}")
        else:
            print("📌 Evento sin cédula (otro tipo de evento)")
        
        return JsonResponse({'status': 'ok'})
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'status': 'error'}, status=500)