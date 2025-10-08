# flota/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
import json
from .models import Vehiculo, CentroOperacional, Mantenimiento, TipoMantenimiento, Proveedor
from .forms import VehiculoForm, ActualizarKilometrajeForm, MantenimientoForm, CompletarMantenimientoForm



# ==================== DASHBOARD ====================
@login_required
def dashboard_view(request):
    """Centro de Control Operativo - Vista Principal"""
    
    # Obtener datos REALES de la base de datos
    vehiculos = Vehiculo.objects.all()
    centros = CentroOperacional.objects.all()
    
    # Estadísticas generales
    total = vehiculos.count()
    operativos = vehiculos.filter(estado='operativo').count()
    mantenimiento = vehiculos.filter(estado='mantenimiento').count()
    fuera_servicio = vehiculos.filter(estado='fuera_servicio').count()
    
    # Estadísticas por centro
    centros_data = []
    for centro in centros:
        vehiculos_centro = centro.vehiculos.all()
        operativos_centro = vehiculos_centro.filter(estado='operativo').count()
        mantenimiento_centro = vehiculos_centro.filter(estado='mantenimiento').count()
        fuera_servicio_centro = vehiculos_centro.filter(estado='fuera_servicio').count()
        total_centro = vehiculos_centro.count()
        
        centros_data.append({
            'nombre': centro.nombre,
            'operativos': operativos_centro,
            'mantenimiento': mantenimiento_centro,
            'fuera_servicio': fuera_servicio_centro,
            'total': total_centro,
            'disponibilidad': round((operativos_centro / total_centro) * 100, 1) if total_centro > 0 else 0
        })
    
    # Vehículos por tipo
    gc_total = vehiculos.filter(tipo_capacidad='GC').count()
    mc_total = vehiculos.filter(tipo_capacidad='MC').count()
    
    context = {
        'usuario': request.user,
        'total_vehiculos': total,
        'vehiculos_operativos': operativos,
        'vehiculos_mantenimiento': mantenimiento,
        'vehiculos_fuera_servicio': fuera_servicio,
        'centros_data': centros_data,
        'gc_total': gc_total,
        'mc_total': mc_total,
        'page_title': 'Centro de Control Operativo',
        'centros_data_json': json.dumps(centros_data),
    }
    
    return render(request, 'flota/dashboard.html', context)
# AGREGAR después de dashboard_view en flota/views.py

@login_required
def estadisticas_view(request):
    """Vista de Estadísticas y Gráficos"""
    
    # Obtener datos para gráficos
    vehiculos = Vehiculo.objects.all()
    centros = CentroOperacional.objects.all()
    
    # Estadísticas generales
    total = vehiculos.count()
    operativos = vehiculos.filter(estado='operativo').count()
    mantenimiento = vehiculos.filter(estado='mantenimiento').count()
    fuera_servicio = vehiculos.filter(estado='fuera_servicio').count()
    
    # Por tipo
    gc_total = vehiculos.filter(tipo_capacidad='GC').count()
    mc_total = vehiculos.filter(tipo_capacidad='MC').count()
    
    # Por centro
    centros_data = []
    for centro in centros:
        vehiculos_centro = centro.vehiculos.all()
        operativos_centro = vehiculos_centro.filter(estado='operativo').count()
        mantenimiento_centro = vehiculos_centro.filter(estado='mantenimiento').count()
        fuera_servicio_centro = vehiculos_centro.filter(estado='fuera_servicio').count()
        total_centro = vehiculos_centro.count()
        
        centros_data.append({
            'nombre': centro.nombre,
            'operativos': operativos_centro,
            'mantenimiento': mantenimiento_centro,
            'fuera_servicio': fuera_servicio_centro,
            'total': total_centro,
            'disponibilidad': round((operativos_centro / total_centro) * 100, 1) if total_centro > 0 else 0
        })
    
    import json
    
    context = {
        'total_vehiculos': total,
        'vehiculos_operativos': operativos,
        'vehiculos_mantenimiento': mantenimiento,
        'vehiculos_fuera_servicio': fuera_servicio,
        'gc_total': gc_total,
        'mc_total': mc_total,
        'centros_data': centros_data,
        'centros_data_json': json.dumps(centros_data),
        'page_title': 'Estadísticas',
    }
    
    return render(request, 'flota/estadisticas.html', context)

# ==================== GESTIÓN DE VEHÍCULOS ====================
@login_required
def gestion_vehiculos_view(request):
    """Gestión de Vehículos - Lista completa"""
    vehiculos = Vehiculo.objects.select_related('centro_operacion').all().order_by('patente')
    
    # Filtros
    centro_filter = request.GET.get('centro', '')
    tipo_filter = request.GET.get('tipo', '')
    estado_filter = request.GET.get('estado', '')
    
    if centro_filter:
        vehiculos = vehiculos.filter(centro_operacion__nombre=centro_filter)
    if tipo_filter:
        vehiculos = vehiculos.filter(tipo_capacidad=tipo_filter)
    if estado_filter:
        vehiculos = vehiculos.filter(estado=estado_filter)
    
    context = {
        'vehiculos': vehiculos,
        'centros': CentroOperacional.objects.all(),
        'page_title': 'Gestión de Vehículos',
    }
    
    return render(request, 'flota/vehiculos_lista.html', context)


@login_required
def vehiculo_detalle_view(request, pk):
    """Ver detalle completo de un vehículo"""
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    
    # Mantenimientos del vehículo
    mantenimientos = vehiculo.mantenimientos.select_related(
        'tipo_mantenimiento', 'proveedor'
    ).order_by('-fecha_programada')[:10]
    
    context = {
        'vehiculo': vehiculo,
        'mantenimientos': mantenimientos,
        'page_title': f'Vehículo {vehiculo.patente}',
    }
    
    return render(request, 'flota/vehiculo_detalle.html', context)


@login_required
def vehiculo_crear_view(request):
    """Crear nuevo vehículo"""
    if request.method == 'POST':
        form = VehiculoForm(request.POST, request.FILES)
        if form.is_valid():
            vehiculo = form.save()
            messages.success(request, f'✅ Vehículo {vehiculo.patente} creado exitosamente.')
            return redirect('flota:vehiculo_detalle', pk=vehiculo.pk)
    else:
        form = VehiculoForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Nuevo Vehículo',
        'boton': 'Crear Vehículo',
        'page_title': 'Nuevo Vehículo',
    }
    
    return render(request, 'flota/vehiculo_form.html', context)


@login_required
def vehiculo_editar_view(request, pk):
    """Editar vehículo existente"""
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    
    if request.method == 'POST':
        form = VehiculoForm(request.POST, request.FILES, instance=vehiculo)
        if form.is_valid():
            vehiculo = form.save()
            messages.success(request, f'✅ Vehículo {vehiculo.patente} actualizado exitosamente.')
            return redirect('flota:vehiculo_detalle', pk=vehiculo.pk)
    else:
        form = VehiculoForm(instance=vehiculo)
    
    context = {
        'form': form,
        'vehiculo': vehiculo,
        'titulo': f'Editar Vehículo {vehiculo.patente}',
        'boton': 'Guardar Cambios',
        'page_title': f'Editar {vehiculo.patente}',
    }
    
    return render(request, 'flota/vehiculo_form.html', context)


@login_required
def vehiculo_eliminar_view(request, pk):
    """Eliminar vehículo"""
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    
    if request.method == 'POST':
        patente = vehiculo.patente
        vehiculo.delete()
        messages.success(request, f'✅ Vehículo {patente} eliminado exitosamente.')
        return redirect('flota:vehiculos')
    
    context = {
        'vehiculo': vehiculo,
        'page_title': f'Eliminar {vehiculo.patente}',
    }
    
    return render(request, 'flota/vehiculo_eliminar.html', context)


@login_required
def vehiculo_actualizar_km_view(request, pk):
    """Actualizar kilometraje rápido"""
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    
    if request.method == 'POST':
        form = ActualizarKilometrajeForm(request.POST, instance=vehiculo)
        if form.is_valid():
            vehiculo = form.save()
            messages.success(request, f'✅ Kilometraje de {vehiculo.patente} actualizado a {vehiculo.kilometraje_actual:,} km.')
            return redirect('flota:vehiculo_detalle', pk=vehiculo.pk)
    else:
        form = ActualizarKilometrajeForm(instance=vehiculo)
    
    context = {
        'form': form,
        'vehiculo': vehiculo,
        'page_title': f'Actualizar KM {vehiculo.patente}',
    }
    
    return render(request, 'flota/vehiculo_actualizar_km.html', context)


# ==================== MANTENIMIENTOS ====================
# ==================== MANTENIMIENTOS ====================
@login_required
def mantenimientos_view(request):
    """Sistema de Mantenimientos - Lista completa"""
    mantenimientos = Mantenimiento.objects.select_related(
        'vehiculo', 'tipo_mantenimiento', 'proveedor'
    ).all().order_by('-fecha_programada')
    
    # Filtros
    estado_filter = request.GET.get('estado', '')
    tipo_filter = request.GET.get('tipo', '')
    prioridad_filter = request.GET.get('prioridad', '')
    
    if estado_filter:
        mantenimientos = mantenimientos.filter(estado=estado_filter)
    if tipo_filter:
        mantenimientos = mantenimientos.filter(tipo=tipo_filter)
    if prioridad_filter:
        mantenimientos = mantenimientos.filter(prioridad=prioridad_filter)
    
    # Estadísticas
    total = Mantenimiento.objects.count()
    programados = Mantenimiento.objects.filter(estado='programado').count()
    en_proceso = Mantenimiento.objects.filter(estado='en_proceso').count()
    completados = Mantenimiento.objects.filter(estado='completado').count()
    
    context = {
        'mantenimientos': mantenimientos,
        'total': total,
        'programados': programados,
        'en_proceso': en_proceso,
        'completados': completados,
        'page_title': 'Mantenimientos',
    }
    
    return render(request, 'flota/mantenimientos.html', context)


@login_required
def mantenimiento_crear_view(request):
    """Programar nuevo mantenimiento"""
    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        if form.is_valid():
            mantenimiento = form.save(commit=False)
            mantenimiento.usuario_programacion = request.user
            mantenimiento.save()
            messages.success(request, f'✅ Mantenimiento programado exitosamente para {mantenimiento.vehiculo.patente}.')
            return redirect('flota:mantenimiento_detalle', pk=mantenimiento.pk)
    else:
        vehiculo_id = request.GET.get('vehiculo')
        initial = {}
        if vehiculo_id:
            try:
                vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
                initial['vehiculo'] = vehiculo
                initial['kilometraje_programado'] = vehiculo.kilometraje_actual
            except Vehiculo.DoesNotExist:
                pass
        
        form = MantenimientoForm(initial=initial)
    
    context = {
        'form': form,
        'titulo': 'Programar Mantenimiento',
        'boton': 'Programar Mantenimiento',
        'page_title': 'Nuevo Mantenimiento',
    }
    
    return render(request, 'flota/mantenimiento_form.html', context)


@login_required
def mantenimiento_detalle_view(request, pk):
    """Ver detalle de un mantenimiento"""
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    
    context = {
        'mantenimiento': mantenimiento,
        'page_title': f'Mantenimiento {mantenimiento.vehiculo.patente}',
    }
    
    return render(request, 'flota/mantenimiento_detalle.html', context)


@login_required
def mantenimiento_completar_view(request, pk):
    """Completar un mantenimiento"""
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    
    if request.method == 'POST':
        form = CompletarMantenimientoForm(request.POST, instance=mantenimiento)
        if form.is_valid():
            mantenimiento = form.save()
            
            # Generar número de reporte automático
            numero_reporte = f"MT-2025-{mantenimiento.pk:04d}"
            
            # Mensaje de éxito con simulación de reporte
            mensaje_html = f"""
            <strong>✅ Mantenimiento completado exitosamente</strong><br><br>
            <div style='background: #f0f9ff; padding: 15px; border-left: 4px solid #3b82f6; margin-top: 10px;'>
                <strong>📊 Reporte Automático Generado</strong><br>
                <hr style='margin: 8px 0; border-color: #bfdbfe;'>
                <strong>Número:</strong> {numero_reporte}<br>
                <strong>📧 Enviado a:</strong> Jefe de Mantenimiento, Gerente de Operaciones<br>
                <strong>📎 Formatos:</strong> PDF, Excel (.xlsx)<br>
                <strong>💾 Ubicación:</strong> Sistema DocuTrans → Mantenimientos 2025<br>
                <small style='color: #64748b; margin-top: 8px; display: block;'>
                    <em>En el sistema real, este reporte se enviaría automáticamente por email y se almacenaría en el servidor.</em>
                </small>
            </div>
            """
            
            messages.success(request, mensaje_html, extra_tags='safe')
            return redirect('flota:mantenimiento_detalle', pk=mantenimiento.pk)
    else:
        form = CompletarMantenimientoForm(instance=mantenimiento)
    
    context = {
        'form': form,
        'mantenimiento': mantenimiento,
        'page_title': f'Completar Mantenimiento {mantenimiento.vehiculo.patente}',
    }
    
    return render(request, 'flota/mantenimiento_completar.html', context)

@login_required
def mantenimiento_reporte_view(request, pk):
    """Ver detalle del reporte de un mantenimiento completado"""
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    
    if mantenimiento.estado != 'completado':
        messages.warning(request, 'Este mantenimiento aún no está completado. No hay reporte disponible.')
        return redirect('flota:mantenimiento_detalle', pk=pk)
    
    # Calcular diferencia de costo
    diferencia = None
    porcentaje_diferencia = None
    if mantenimiento.costo_real and mantenimiento.costo_estimado:
        diferencia = mantenimiento.costo_real - mantenimiento.costo_estimado
        porcentaje_diferencia = (diferencia / mantenimiento.costo_estimado) * 100
    
    context = {
        'mantenimiento': mantenimiento,
        'diferencia_costo': diferencia,
        'porcentaje_diferencia': porcentaje_diferencia,
        'page_title': f'Reporte {mantenimiento.numero_reporte()}',
    }
    
    return render(request, 'flota/mantenimiento_reporte.html', context)


@login_required
def mantenimiento_eliminar_view(request, pk):
    """Eliminar mantenimiento"""
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    
    if request.method == 'POST':
        vehiculo = mantenimiento.vehiculo.patente
        mantenimiento.delete()
        messages.success(request, f'✅ Mantenimiento de {vehiculo} eliminado.')
        return redirect('flota:mantenimientos')
    
    context = {
        'mantenimiento': mantenimiento,
        'page_title': 'Eliminar Mantenimiento',
    }
    
    return render(request, 'flota/mantenimiento_eliminar.html', context)


# ==================== REPORTES ====================
# ==================== REPORTES ====================
@login_required
def reportes_view(request):
    """Sistema de Reportes"""
    
    # Si viene una acción de generar reporte
    if request.GET.get('generar'):
        tipo_reporte = request.GET.get('tipo')
        
        # Simular generación según tipo
        mensajes_reporte = {
            'vehiculos': {
                'titulo': 'Reporte de Flota Vehicular',
                'destinatarios': 'Gerente de Operaciones, Jefe de Flota',
                'copia': 'Director General, Contador',
                'formatos': 'PDF, Excel (.xlsx)',
                'contenido': 'Listado completo de vehículos, estado, kilometraje, centro operacional y alertas de mantenimiento'
            },
            'mantenimientos': {
                'titulo': 'Reporte de Mantenimientos',
                'destinatarios': 'Jefe de Mantenimiento, Gerente de Operaciones',
                'copia': 'Director General, Jefe de Compras',
                'formatos': 'PDF, Excel (.xlsx)',
                'contenido': 'Historial de mantenimientos, costos reales vs estimados, proveedores utilizados y próximos servicios programados'
            },
            'costos': {
                'titulo': 'Análisis de Costos Operacionales',
                'destinatarios': 'Gerente Financiero, Director General',
                'copia': 'Contador, Gerente de Operaciones',
                'formatos': 'PDF, Excel (.xlsx), Planilla de Cálculo Google Sheets',
                'contenido': 'Costos por vehículo, costos por centro, análisis de desviaciones presupuestarias y proyecciones mensuales'
            },
            'rendimiento': {
                'titulo': 'Indicadores de Rendimiento (KPIs)',
                'destinatarios': 'Director General, Gerente de Operaciones',
                'copia': 'Todos los jefes de área',
                'formatos': 'PDF con gráficos, Dashboard interactivo Excel',
                'contenido': 'Disponibilidad de flota, cumplimiento de mantenimientos, eficiencia operacional y comparativas por centro'
            },
            'alertas': {
                'titulo': 'Reporte de Alertas y Acciones Requeridas',
                'destinatarios': 'Jefe de Flota, Jefe de Mantenimiento',
                'copia': 'Gerente de Operaciones',
                'formatos': 'PDF, Email HTML',
                'contenido': 'Vehículos con alertas críticas, mantenimientos vencidos, acciones pendientes y recomendaciones urgentes'
            }
        }
        
        info = mensajes_reporte.get(tipo_reporte, {})
        
        messages.success(
            request,
            f'✅ Reporte "{info.get("titulo", "")}" generado exitosamente. '
            f'En la versión completa se enviaría automáticamente.'
        )
        
        context = {
            'reporte_generado': True,
            'info_reporte': info,
            'page_title': 'Reportes',
        }
        
        return render(request, 'flota/reportes.html', context)
    
    # Vista normal
    context = {
        'page_title': 'Reportes',
    }
    
    return render(request, 'flota/reportes.html', context)
# ==================== ALERTAS ====================
@login_required
def alertas_view(request):
    """Centro de Alertas Mejorado"""
    
    # Vehículos que necesitan mantenimiento pronto
    vehiculos_alerta = []
    for vehiculo in Vehiculo.objects.filter(estado='operativo'):
        km_restantes = vehiculo.km_hasta_mantenimiento()
        if km_restantes <= 2000:
            nivel = 'critico' if km_restantes <= 500 else 'alta' if km_restantes <= 1000 else 'media'
            vehiculos_alerta.append({
                'vehiculo': vehiculo,
                'km_restantes': km_restantes,
                'nivel': nivel,
                'tipo': 'mantenimiento',
                'mensaje': f'Mantenimiento próximo en {km_restantes} km'
            })
    
    # Vehículos en mantenimiento hace mucho tiempo
    mantenimientos_activos = Mantenimiento.objects.filter(
        estado__in=['programado', 'en_proceso']
    ).select_related('vehiculo')
    
    for mant in mantenimientos_activos:
        if mant.estado == 'en_proceso':
            vehiculos_alerta.append({
                'vehiculo': mant.vehiculo,
                'nivel': 'media',
                'tipo': 'en_proceso',
                'mensaje': f'Mantenimiento en proceso desde {mant.fecha_programada}'
            })
    
    # Filtros
    nivel_filter = request.GET.get('nivel', '')
    if nivel_filter:
        vehiculos_alerta = [a for a in vehiculos_alerta if a['nivel'] == nivel_filter]
    
    # Contar por nivel
    criticas = len([a for a in vehiculos_alerta if a['nivel'] == 'critico'])
    altas = len([a for a in vehiculos_alerta if a['nivel'] == 'alta'])
    medias = len([a for a in vehiculos_alerta if a['nivel'] == 'media'])
    
    context = {
        'vehiculos_alerta': vehiculos_alerta,
        'total_alertas': len(vehiculos_alerta),
        'alertas_criticas': criticas,
        'alertas_altas': altas,
        'alertas_medias': medias,
        'page_title': 'Alertas',
    }
    
    return render(request, 'flota/alertas.html', context)


# ==================== API ====================
@login_required
def api_alertas_count(request):
    """API para contar alertas activas"""
    count = 0
    
    # Contar vehículos que necesitan mantenimiento
    for vehiculo in Vehiculo.objects.filter(estado='operativo'):
        if vehiculo.km_hasta_mantenimiento() <= 2000:
            count += 1
    
    return JsonResponse({'count': count})


# ==================== USUARIOS ====================
@login_required
def cambiar_usuario_view(request):
    """Cerrar sesión para cambiar de usuario"""
    logout(request)
    messages.success(request, 'Sesión cerrada. Puedes iniciar sesión con otro usuario.')
    return redirect('/admin/login/')