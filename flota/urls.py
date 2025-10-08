# flota/urls.py
from django.urls import path
from . import views

app_name = 'flota'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    path('estadisticas/', views.estadisticas_view, name='estadisticas'),
    
    # Vehículos
    path('vehiculos/', views.gestion_vehiculos_view, name='vehiculos'),
    path('vehiculos/crear/', views.vehiculo_crear_view, name='vehiculo_crear'),
    path('vehiculos/<int:pk>/', views.vehiculo_detalle_view, name='vehiculo_detalle'),
    path('vehiculos/<int:pk>/editar/', views.vehiculo_editar_view, name='vehiculo_editar'),
    path('vehiculos/<int:pk>/eliminar/', views.vehiculo_eliminar_view, name='vehiculo_eliminar'),
    path('vehiculos/<int:pk>/actualizar-km/', views.vehiculo_actualizar_km_view, name='vehiculo_actualizar_km'),
    
    # Mantenimientos
    path('mantenimientos/', views.mantenimientos_view, name='mantenimientos'),
    path('mantenimientos/crear/', views.mantenimiento_crear_view, name='mantenimiento_crear'),
    path('mantenimientos/<int:pk>/', views.mantenimiento_detalle_view, name='mantenimiento_detalle'),
    path('mantenimientos/<int:pk>/completar/', views.mantenimiento_completar_view, name='mantenimiento_completar'),
    path('mantenimientos/<int:pk>/eliminar/', views.mantenimiento_eliminar_view, name='mantenimiento_eliminar'),
    
    # API
    path('api/alertas-count/', views.api_alertas_count, name='api_alertas_count'),

    # Otras secciones
    path('reportes/', views.reportes_view, name='reportes'),
    path('alertas/', views.alertas_view, name='alertas'),
    path('cambiar-usuario/', views.cambiar_usuario_view, name='cambiar_usuario'),
]