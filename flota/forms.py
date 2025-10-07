# flota/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
from .models import Vehiculo, CentroOperacional


class VehiculoForm(forms.ModelForm):
    """Formulario para registro y edición de vehículos."""
    
    class Meta:
        model = Vehiculo
        fields = [
            'patente', 'marca', 'modelo', 'año', 'tipo_capacidad',
            'centro_operacion', 'kilometraje_actual', 'estado',
            'numero_chasis', 'numero_motor', 'valor_adquisicion',
            'fecha_adquisicion', 'observaciones'
        ]
        
        widgets = {
            'patente': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ej: AB-1234',
                'pattern': '[A-Z]{2}-[0-9]{4}',
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ej: Mercedes-Benz'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ej: Actros 2644'
            }),
            'año': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'min': 2000,
                'max': 2030
            }),
            'tipo_capacidad': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'centro_operacion': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'kilometraje_actual': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ej: 150000',
                'min': 0
            }),
            'estado': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'numero_chasis': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de chasis (opcional)'
            }),
            'numero_motor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de motor (opcional)'
            }),
            'valor_adquisicion': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Valor en CLP',
                'step': '100000'
            }),
            'fecha_adquisicion': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
        }
        
        labels = {
            'patente': 'Patente del Vehículo *',
            'marca': 'Marca *',
            'modelo': 'Modelo *',
            'año': 'Año de Fabricación *',
            'tipo_capacidad': 'Tipo de Capacidad *',
            'centro_operacion': 'Centro Operacional *',
            'kilometraje_actual': 'Kilometraje Actual *',
            'estado': 'Estado Actual *',
            'numero_chasis': 'Número de Chasis',
            'numero_motor': 'Número de Motor',
            'valor_adquisicion': 'Valor de Adquisición (CLP)',
            'fecha_adquisicion': 'Fecha de Adquisición',
            'observaciones': 'Observaciones',
        }
    
    def clean_patente(self):
        """Validación de patente chilena."""
        patente = self.cleaned_data['patente'].upper()
        
        if not re.match(r'^[A-Z]{2}-[0-9]{4}$', patente):
            raise ValidationError('Formato de patente inválido. Use formato chileno: XX-1234')
        
        # Verificar que no exista otra patente igual (excepto si es edición)
        queryset = Vehiculo.objects.filter(patente=patente)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError('Ya existe un vehículo con esta patente.')
        
        return patente
    
    def clean_año(self):
        """Validación del año del vehículo."""
        año = self.cleaned_data['año']
        año_actual = timezone.now().year
        
        if año < 2000:
            raise ValidationError('El año debe ser mayor o igual a 2000.')
        
        if año > año_actual + 1:
            raise ValidationError(f'El año no puede ser mayor a {año_actual + 1}.')
        
        return año
    
    def clean_kilometraje_actual(self):
        """Validación del kilometraje."""
        kilometraje = self.cleaned_data['kilometraje_actual']
        
        if kilometraje < 0:
            raise ValidationError('El kilometraje no puede ser negativo.')
        
        if kilometraje > 2000000:
            raise ValidationError('El kilometraje parece excesivo. Verifique el valor.')
        
        return kilometraje


class ActualizarKilometrajeForm(forms.ModelForm):
    """Formulario rápido para actualizar solo el kilometraje"""
    
    class Meta:
        model = Vehiculo
        fields = ['kilometraje_actual']
        
        widgets = {
            'kilometraje_actual': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'min': 0
            })
        }
        
        labels = {
            'kilometraje_actual': 'Nuevo Kilometraje'
        }
    
    def clean_kilometraje_actual(self):
        kilometraje = self.cleaned_data['kilometraje_actual']
        
        if self.instance.kilometraje_actual and kilometraje < self.instance.kilometraje_actual:
            raise ValidationError(
                f'El nuevo kilometraje ({kilometraje:,} km) no puede ser menor al actual ({self.instance.kilometraje_actual:,} km).'
            )
        
        return kilometraje