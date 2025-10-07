# flota/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Vehiculo, CentroOperacional, Mantenimiento, TipoMantenimiento, Proveedor
from .forms import VehiculoForm, ActualizarKilometrajeForm


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
    }
    
    return render(request, 'flota/dashboard.html', context)


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
@login_required
def mantenimientos_view(request):
    """Sistema de Mantenimientos"""
    mantenimientos = Mantenimiento.objects.select_related(
        'vehiculo', 'tipo_mantenimiento', 'proveedor'
    ).all().order_by('-fecha_programada')[:20]
    
    context = {
        'mantenimientos': mantenimientos,
        'page_title': 'Mantenimientos',
    }
    
    return render(request, 'flota/mantenimientos.html', context)


# ==================== REPORTES ====================
@login_required
def reportes_view(request):
    """Centro de Reportes"""
    context = {
        'page_title': 'Reportes',
    }
    return render(request, 'flota/reportes.html', context)


# ==================== ALERTAS ====================
@login_required
def alertas_view(request):
    """Centro de Alertas"""
    # Vehículos que necesitan mantenimiento pronto
    vehiculos_alerta = []
    for vehiculo in Vehiculo.objects.filter(estado='operativo'):
        km_restantes = vehiculo.km_hasta_mantenimiento()
        if km_restantes <= 2000:
            vehiculos_alerta.append({
                'vehiculo': vehiculo,
                'km_restantes': km_restantes,
                'nivel': 'critico' if km_restantes <= 500 else 'alerta'
            })
    
    context = {
        'vehiculos_alerta': vehiculos_alerta,
        'page_title': 'Alertas',
    }
    return render(request, 'flota/alertas.html', context)


# ==================== USUARIOS ====================
@login_required
def cambiar_usuario_view(request):
    """Cerrar sesión para cambiar de usuario"""
    logout(request)
    messages.success(request, 'Sesión cerrada. Puedes iniciar sesión con otro usuario.')
    return redirect('/admin/login/')