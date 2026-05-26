from datetime import date
from django.db.models import Q

def combinar_historial(visitantes, registros_manual, filtro_tipo):
    """
    Combina visitantes y registros manuales en una sola lista
    
    Args:
        visitantes: QuerySet de visitantes
        registros_manual: QuerySet de registros manuales
        filtro_tipo: 'Visitante', 'Manual' o '' para ambos
    
    Returns:
        list: Lista combinada y ordenada
    """
    # Filtrar por tipo
    if filtro_tipo == 'Visitante':
        registros_manual = []
    elif filtro_tipo == 'Manual':
        visitantes = []
    
    registros_unificados = []
    
    # Agregar visitantes
    for v in visitantes:
        registros_unificados.append({
            'tipo': 'visitante',
            'objeto': v,
            'fecha_orden': v.id_asistencia_sede.fecha if v.id_asistencia_sede else date.min,
            'nombre': v.nombre,
            'apellido': v.apellido,
            'cedula': v.cedula,
            'motivo': v.motivo,
            'fecha': v.id_asistencia_sede.fecha if v.id_asistencia_sede else None,
            'hora_entrada': v.id_asistencia_sede.hora_entrada if v.id_asistencia_sede else None,
            'hora_salida': v.id_asistencia_sede.hora_salida if v.id_asistencia_sede else None,
            'estado': 'dentro' if (v.id_asistencia_sede and not v.id_asistencia_sede.hora_salida) else 'fuera',
        })
    
    # Agregar registros manuales
    for r in registros_manual:
        registros_unificados.append({
            'tipo': 'manual',
            'objeto': r,
            'fecha_orden': r.fecha,
            'nombre': r.nombres or (r.id_usuario.nombre if r.id_usuario else ''),
            'apellido': r.id_usuario.apellido if r.id_usuario else '',
            'cedula': r.cedula or r.documento,
            'motivo': r.motivo,
            'fecha': r.fecha,
            'hora': r.hora,
            'tipo_movimiento': r.tipo_movimiento,
            'usuario_nombre': f"{r.id_usuario.nombre} {r.id_usuario.apellido}" if r.id_usuario else '',
        })
    
    # Ordenar por fecha descendente
    registros_unificados.sort(key=lambda x: x['fecha_orden'] or date.min, reverse=True)
    
    return registros_unificados


def aplicar_filtros_historial(visitantes, registros_manual, nombre, cedula, fecha_desde, fecha_hasta):
    """
    Aplica filtros a visitantes y registros manuales
    
    Returns:
        tuple: (visitantes_filtrados, registros_filtrados)
    """
    # Filtrar visitantes
    if nombre:
        visitantes = visitantes.filter(
            Q(nombre__icontains=nombre) | Q(apellido__icontains=nombre)
        )
    
    if cedula:
        visitantes = visitantes.filter(cedula__icontains=cedula)
    
    if fecha_desde:
        visitantes = visitantes.filter(id_asistencia_sede__fecha__gte=fecha_desde)
    
    if fecha_hasta:
        visitantes = visitantes.filter(id_asistencia_sede__fecha__lte=fecha_hasta)
    
    # Filtrar registros manuales
    if nombre:
        registros_manual = registros_manual.filter(
            Q(nombres__icontains=nombre) |
            Q(id_usuario__nombre__icontains=nombre) |
            Q(id_usuario__apellido__icontains=nombre)
        )
    
    if cedula:
        registros_manual = registros_manual.filter(
            Q(cedula__icontains=cedula) | Q(documento__icontains=cedula)
        )
    
    if fecha_desde:
        registros_manual = registros_manual.filter(fecha__gte=fecha_desde)
    
    if fecha_hasta:
        registros_manual = registros_manual.filter(fecha__lte=fecha_hasta)
    
    return visitantes, registros_manual