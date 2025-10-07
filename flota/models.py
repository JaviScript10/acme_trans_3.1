# flota/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


class CentroOperacional(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    direccion = models.TextField(verbose_name="Dirección")
    ciudad = models.CharField(max_length=50, verbose_name="Ciudad")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    responsable = models.CharField(max_length=100, verbose_name="Responsable")
    capacidad_maxima = models.IntegerField(default=20, verbose_name="Capacidad Máxima")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Centro Operacional"
        verbose_name_plural = "Centros Operacionales"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def vehiculos_count(self):
        return self.vehiculos.count()
    
    def vehiculos_operativos(self):
        return self.vehiculos.filter(estado='operativo').count()
    
    def disponibilidad_porcentaje(self):
        total = self.vehiculos.count()
        operativos = self.vehiculos_operativos()
        return round((operativos / total) * 100, 1) if total > 0 else 0


class Vehiculo(models.Model):
    ESTADO_CHOICES = [
        ('operativo', 'Operativo'),
        ('mantenimiento', 'En Mantenimiento'),
        ('fuera_servicio', 'Fuera de Servicio'),
    ]
    
    TIPO_CAPACIDAD_CHOICES = [
        ('GC', 'Gran Capacidad'),
        ('MC', 'Mediana Capacidad'),
    ]
    
    # Campos principales
    patente = models.CharField(max_length=10, unique=True, verbose_name="Patente")
    marca = models.CharField(max_length=50, verbose_name="Marca")
    modelo = models.CharField(max_length=50, verbose_name="Modelo")
    año = models.IntegerField(verbose_name="Año")
    tipo_capacidad = models.CharField(
        max_length=2, 
        choices=TIPO_CAPACIDAD_CHOICES, 
        default='MC',
        verbose_name="Tipo de Capacidad"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='operativo',
        verbose_name="Estado"
    )
    kilometraje_actual = models.IntegerField(default=0, verbose_name="Kilometraje Actual")
    centro_operacion = models.ForeignKey(
        CentroOperacional, 
        on_delete=models.CASCADE, 
        related_name='vehiculos',
        verbose_name="Centro Operacional"
    )
    
    # Datos técnicos opcionales
    numero_chasis = models.CharField(max_length=50, blank=True, verbose_name="Número de Chasis")
    numero_motor = models.CharField(max_length=50, blank=True, verbose_name="Número de Motor")
    
    # Datos financieros opcionales
    valor_adquisicion = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="Valor de Adquisición"
    )
    fecha_adquisicion = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Fecha de Adquisición"
    )
    
    # Documentación
    imagen = models.ImageField(
        upload_to='vehiculos/', 
        null=True, 
        blank=True,
        verbose_name="Foto del Vehículo"
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    
    # Metadatos
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ['patente']
    
    def __str__(self):
        return f"{self.patente} - {self.marca} {self.modelo}"
    
    def get_absolute_url(self):
        return reverse('flota:vehiculo_detail', kwargs={'pk': self.pk})
    
    def proximo_mantenimiento_km(self):
        """Calcula el próximo mantenimiento cada 10,000 km"""
        return ((self.kilometraje_actual // 10000) + 1) * 10000
    
    def km_hasta_mantenimiento(self):
        """Kilómetros restantes hasta próximo mantenimiento"""
        return self.proximo_mantenimiento_km() - self.kilometraje_actual
    
    def necesita_mantenimiento(self):
        """Verifica si necesita mantenimiento pronto (menos de 500 km)"""
        return self.km_hasta_mantenimiento() <= 500


class TipoMantenimiento(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    frecuencia_km = models.IntegerField(
        help_text="Cada cuántos km se debe realizar",
        verbose_name="Frecuencia (km)"
    )
    costo_estimado = models.DecimalField(
        max_digits=10, 
        decimal_places=0,
        verbose_name="Costo Estimado"
    )
    tiempo_estimado_horas = models.IntegerField(verbose_name="Tiempo Estimado (horas)")
    es_preventivo = models.BooleanField(default=True, verbose_name="¿Es Preventivo?")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Tipo de Mantenimiento"
        verbose_name_plural = "Tipos de Mantenimiento"
    
    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    rut = models.CharField(max_length=12, verbose_name="RUT")
    direccion = models.TextField(verbose_name="Dirección")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email")
    contacto_principal = models.CharField(max_length=100, verbose_name="Contacto Principal")
    especialidad = models.CharField(max_length=100, verbose_name="Especialidad")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
    
    def __str__(self):
        return self.nombre


class Mantenimiento(models.Model):
    ESTADO_CHOICES = [
        ('programado', 'Programado'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    TIPO_CHOICES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    vehiculo = models.ForeignKey(
        Vehiculo, 
        on_delete=models.CASCADE, 
        related_name='mantenimientos',
        verbose_name="Vehículo"
    )
    tipo_mantenimiento = models.ForeignKey(
        TipoMantenimiento, 
        on_delete=models.CASCADE,
        verbose_name="Tipo de Mantenimiento"
    )
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.CASCADE,
        verbose_name="Proveedor"
    )
    tipo = models.CharField(
        max_length=20, 
        choices=TIPO_CHOICES, 
        default='preventivo',
        verbose_name="Tipo"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='programado',
        verbose_name="Estado"
    )
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='media',
        verbose_name="Prioridad"
    )
    fecha_programada = models.DateField(verbose_name="Fecha Programada")
    fecha_realizacion = models.DateField(null=True, blank=True, verbose_name="Fecha de Realización")
    kilometraje_programado = models.IntegerField(verbose_name="Kilometraje Programado")
    costo_estimado = models.DecimalField(
        max_digits=10, 
        decimal_places=0,
        verbose_name="Costo Estimado"
    )
    costo_real = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        null=True, 
        blank=True,
        verbose_name="Costo Real"
    )
    tiempo_estimado_horas = models.IntegerField(
        default=4,
        verbose_name="Tiempo Estimado (horas)"
    )
    descripcion = models.TextField(verbose_name="Descripción del Trabajo")
    observaciones_programacion = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    usuario_programacion = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='mantenimientos_programados',
        verbose_name="Usuario que Programó"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering = ['-fecha_programada']
    
    def __str__(self):
        return f"{self.vehiculo.patente} - {self.tipo_mantenimiento.nombre}"