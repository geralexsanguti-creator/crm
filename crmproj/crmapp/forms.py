from django import forms
from .models import Producto, Venta, Cliente, Usuario, Equipo, EmpresaSocia, Role, Comision, ReglaComision
from django.contrib.auth.forms import AuthenticationForm
import datetime


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label = 'Nombre usuario',
        widget= forms.TextInput(attrs={
            'class' : 'form-control',
            'placeholder' : 'Ingrese nombre usuario'
        })
    )

    password = forms.CharField(
        label = 'Contraseña',
        widget= forms.PasswordInput(attrs={
            'class' : 'form-control',
            'placeholder' : 'Ingrese contraseña'
        })
    )

    class Meta:

        model = Usuario
        fields = ['username', 'password']

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'descripcion', 'precio_base', 'empresa']
        widgets = {
            'nombre_producto': forms.TextInput(attrs={
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descripción detallada del producto...'
            }),
            'precio_base': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
        }
    
    def clean_precio_base(self):
        precio_base = self.cleaned_data.get('precio_base')
        if precio_base and precio_base < 0:
            raise forms.ValidationError("El precio base no puede ser negativo.")
        return precio_base

class EmpresaSociaForm(forms.ModelForm):
    informacion_adicional = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Información adicional sobre la empresa (opcional)"
    )
    
    class Meta:
        model = EmpresaSocia
        fields = ['nombre_empresa', 'comision_aplicable', 'contacto_email', 'telefono']
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={
                'placeholder': 'Nombre de la empresa',
                'class': 'input input-bordered w-full'
            }),
            'comision_aplicable': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'class': 'input input-bordered w-full'
            }),
            'contacto_email': forms.EmailInput(attrs={
                'placeholder': 'contacto@empresa.com',
                'class': 'input input-bordered w-full'
            }),
            'telefono': forms.TextInput(attrs={
                'placeholder': '+1 234 567 8900',
                'class': 'input input-bordered w-full'
            }),
        }
    
    def clean_comision_aplicable(self):
        comision = self.cleaned_data.get('comision_aplicable')
        if comision is not None:
            if comision < 0:
                raise forms.ValidationError("La comisión no puede ser negativa.")
            if comision > 100:
                raise forms.ValidationError("La comisión no puede ser mayor al 100%.")
        return comision
    
    def clean_nombre_empresa(self):
        nombre = self.cleaned_data.get('nombre_empresa')
        if EmpresaSocia.objects.filter(nombre_empresa__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe una empresa con este nombre.")
        return nombre

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['producto', 'cliente', 'usuario', 'fecha_inicio', 'fecha_fin', 'estado', 'monto_venta']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'input input-bordered w-full',
                'required': True
            }),
            'fecha_fin': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'input input-bordered w-full'
            }),
            'monto_venta': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0',
                'class': 'input input-bordered w-full',
                'required': True
            }),
            'producto': forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'required': True
            }),
            'cliente': forms.Select(attrs={
                'class': 'select select-bordered w-full', 
                'required': True
            }),
            'usuario': forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'required': True
            }),
            'estado': forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'required': True
            }),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre_cliente', 'email', 'telefono', 'direccion']
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Nombre completo del cliente',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'cliente@email.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '+1 234 567 8900'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Dirección completa del cliente...'
            }),
        }
    
    def clean_nombre_cliente(self):
        nombre = self.cleaned_data.get('nombre_cliente')
        if not nombre or nombre.strip() == '':
            raise forms.ValidationError("El nombre del cliente es obligatorio.")
        return nombre.strip()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and email.strip() == '':
            return None  # Convertir string vacío a None
        return email
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and telefono.strip() == '':
            return None  # Convertir string vacío a None
        return telefono

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre_equipo', 'descripcion']
        widgets = {
            'nombre_equipo': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ingrese el nombre del equipo'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered h-24 w-full',
                'placeholder': 'Ingrese una descripción del equipo',
                'rows': 4
            }),
        }

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Usuario
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['role_name', 'productos', 'ventas', 'clientes', 'empresas', 'comisiones', 'regla_comisiones', 'equipos']

class ComisionForm(forms.ModelForm):
    class Meta:
        model = Comision
        fields = ['usuario', 'venta', 'regla', 'monto_comision', 'estado', 'fecha_pagada']
        widgets = {
            'usuario': forms.Select(attrs={
                'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'venta': forms.Select(attrs={
                'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'regla': forms.Select(attrs={
                'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'monto_comision': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 pl-8',
                'step': '0.01',
                'min': '0'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'fecha_pagada': forms.DateInput(attrs={
                'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date'
            }),
        }
    
    def clean_monto_comision(self):
        monto = self.cleaned_data.get('monto_comision')
        if monto and monto <= 0:
            raise forms.ValidationError("El monto de comisión debe ser mayor a 0.")
        return monto
    
    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        fecha_pagada = cleaned_data.get('fecha_pagada')
        
        # Validar que si el estado es Pagada, tenga fecha de pago
        if estado == 'Pagada' and not fecha_pagada:
            raise forms.ValidationError({
                'fecha_pagada': 'Debe especificar una fecha de pago cuando el estado es "Pagada".'
            })
        
        return cleaned_data