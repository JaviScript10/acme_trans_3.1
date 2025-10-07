# flota/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CentroOperacional, Vehiculo, TipoMantenimiento, 
    Proveedor, Mantenimiento
)


@admin.register(CentroOperacional)
class CentroOperacionalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ciudad', 'responsable', 'vehiculos_count', 'disponibilidad_display', 'activo']
    list_filter = ['activo', 'ciudad']
    search_fields = ['nombre', 'ciudad', 'responsable']
    ordering = ['nombre']
    
    def vehiculos_count(self, obj):
        return obj.vehiculos.count()
    vehiculos_count.short_description = 'Vehículos'
    
    def disponibilidad_display(self, obj):
        disponibilidad = obj.disponibilidad_porcentaje()
        if disponibilidad >= 90:
            color = 'green'
        elif disponibilidad >= 75:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, disponibilidad
        )
    disponibilidad_display.short_description = 'Disponibilidad'


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = [
        'patente', 'marca_modelo', 'tipo_capacidad', 'centro_operacion', 
        'kilometraje_actual', 'estado_display'
    ]
    list_filter = ['estado', 'tipo_capacidad', 'centro_operacion', 'marca']
    search_fields = ['patente', 'marca', 'modelo', 'numero_chasis']
    ordering = ['patente']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('patente', 'marca', 'modelo', 'año', 'tipo_capacidad')
        }),
        ('Operación', {
            'fields': ('centro_operacion', 'estado', 'kilometraje_actual')
        }),
        ('Datos Técnicos', {
            'fields': ('numero_chasis', 'numero_motor'),
            'classes': ('collapse',)
        }),
        ('Datos Financieros', {
            'fields': ('valor_adquisicion', 'fecha_adquisicion'),
            'classes': ('collapse',)
        }),
        ('Documentación', {
            'fields': ('imagen', 'observaciones'),
            'classes': ('collapse',)
        }),
    )
    
    def marca_modelo(self, obj):
        return f"{obj.marca} {obj.modelo} ({obj.año})"
    marca_modelo.short_description = 'Marca/Modelo'
    
    def estado_display(self, obj):
        colores = {
            'operativo': 'green',
            'mantenimiento': 'orange',
            'fuera_servicio': 'red',
        }
        color = colores.get(obj.estado, 'black')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_display.short_description = 'Estado'


@admin.register(TipoMantenimiento)
class TipoMantenimientoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'frecuencia_km', 'costo_estimado', 'tiempo_estimado_horas', 'es_preventivo', 'activo']
    list_filter = ['es_preventivo', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rut', 'especialidad', 'telefono', 'email', 'activo']
    list_filter = ['activo', 'especialidad']
    search_fields = ['nombre', 'rut', 'email']
    ordering = ['nombre']


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = [
        'vehiculo', 'tipo_mantenimiento', 'tipo', 'prioridad_display',
        'fecha_programada', 'estado_display', 'costo_estimado'
    ]
    list_filter = ['estado', 'tipo', 'prioridad', 'fecha_programada']
    search_fields = ['vehiculo__patente', 'tipo_mantenimiento__nombre', 'descripcion']
    ordering = ['-fecha_programada']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('vehiculo', 'tipo_mantenimiento', 'proveedor', 'tipo', 'estado', 'prioridad')
        }),
        ('Programación', {
            'fields': ('fecha_programada', 'kilometraje_programado', 'costo_estimado', 'tiempo_estimado_horas', 'descripcion', 'observaciones_programacion', 'usuario_programacion')
        }),
    )
    
    def prioridad_display(self, obj):
        colores = {
            'baja': 'green',
            'media': 'blue',
            'alta': 'orange',
            'critica': 'red'
        }
        color = colores.get(obj.prioridad, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_prioridad_display().upper()
        )
    prioridad_display.short_description = 'Prioridad'
    
    def estado_display(self, obj):
        colores = {
            'programado': 'blue',
            'en_proceso': 'orange',
            'completado': 'green',
            'cancelado': 'red'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_display.short_description = 'Estado'


# Personalizar admin site
admin.site.site_header = 'ACME Trans - Centro de Control Operativo'
admin.site.site_title = 'ACME Trans'
admin.site.index_title = 'Panel de Administración'