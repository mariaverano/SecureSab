from apps.administracion_huella_usuarios.gestor_usuarios.models import registro_actividad
from django.db.models import Q

def obtener_todas_actividades():
    """Obtiene todas las actividades ordenadas por fecha y hora"""
    return registro_actividad.objects.select_related('id_usuario').all().order_by('-fecha', '-hora')

def filtrar_actividades(actividades, buscar, tipo_accion, fecha_desde, fecha_hasta):
    """Aplica filtros a las actividades"""
    if buscar:
        actividades = actividades.filter(
            Q(actividad__icontains=buscar) |
            Q(descripcion__icontains=buscar) |
            Q(id_usuario__nombre__icontains=buscar) |
            Q(id_usuario__apellido__icontains=buscar)
        )
    
    if tipo_accion:
        actividades = actividades.filter(tipo_accion=tipo_accion)
    
    if fecha_desde:
        actividades = actividades.filter(fecha__gte=fecha_desde)
    
    if fecha_hasta:
        actividades = actividades.filter(fecha__lte=fecha_hasta)
    
    return actividades