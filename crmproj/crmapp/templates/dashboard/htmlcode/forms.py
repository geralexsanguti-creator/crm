from django import forms
from .models import Producto, Venta, Cliente, Usuario, Equipo, EmpresaSocia, Comision, ReglaComision
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

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre_equipo', 'descripcion']
        widgets = {
            'nombre_equipo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del equipo'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese una descripción del equipo',
                'rows': 4
            }),
        }
        labels = {
            'nombre_equipo': 'Nombre del Equipo',
            'descripcion': 'Descripción',
        }
        help_texts = {
            'nombre_equipo': 'Ingrese un nombre único para el equipo',
            'descripcion': 'Opcional: describa el propósito o características del equipo',
        }

    def clean_nombre_equipo(self):
        nombre_equipo = self.cleaned_data.get('nombre_equipo')
        if nombre_equipo:
            # Verificar si ya existe un equipo con el mismo nombre (excluyendo el actual si es una edición)
            queryset = Equipo.objects.filter(nombre_equipo__iexact=nombre_equipo)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Ya existe un equipo con este nombre.')
        
        return nombre_equipo

class EmpresaSociaForm(forms.ModelForm):
    class Meta:
        model = EmpresaSocia
        fields = ['nombre_empresa', 'comision_aplicable', 'contacto_email', 'telefono']
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la empresa'
            }),
            'comision_aplicable': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 15.50',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'contacto_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@empresa.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+34 600 123 456'
            }),
        }
        labels = {
            'nombre_empresa': 'Nombre de la Empresa',
            'comision_aplicable': 'Comisión Aplicable (%)',
            'contacto_email': 'Email de Contacto',
            'telefono': 'Teléfono',
        }
        help_texts = {
            'nombre_empresa': 'Nombre único de la empresa socia',
            'comision_aplicable': 'Porcentaje de comisión que se aplicará (0-100%)',
            'contacto_email': 'Email principal de contacto',
            'telefono': 'Número de teléfono de contacto',
        }

    def clean_comision_aplicable(self):
        comision = self.cleaned_data.get('comision_aplicable')
        if comision is not None:
            if comision < 0:
                raise forms.ValidationError('La comisión no puede ser negativa.')
            if comision > 100:
                raise forms.ValidationError('La comisión no puede ser mayor al 100%.')
        return comision


    def clean_nombre_empresa(self):
        nombre_empresa = self.cleaned_data.get('nombre_empresa')
        if nombre_empresa:
            # Verificar si ya existe una empresa con el mismo nombre (excluyendo la actual si es edición)
            queryset = EmpresaSocia.objects.filter(nombre_empresa__iexact=nombre_empresa)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Ya existe una empresa con este nombre.')
        
        return nombre_empresa

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        # Validación básica del teléfono (puedes personalizar según tus necesidades)
        if telefono and len(telefono) < 5:
            raise forms.ValidationError('El número de teléfono parece demasiado corto.')
        return telefono

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'descripcion', 'precio_base', 'empresa']
        widgets = {
            'nombre_producto': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Ingrese el nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Descripción del producto...',
                'rows': 4
            }),
            'precio_base': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'empresa': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
        }
        labels = {
            'nombre_producto': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'precio_base': 'Precio Base',
            'empresa': 'Empresa Socia',
        }
        help_texts = {
            'nombre_producto': 'Nombre único para identificar el producto',
            'descripcion': 'Descripción detallada del producto (opcional)',
            'precio_base': 'Precio base sin comisiones aplicadas',
            'empresa': 'Seleccione la empresa socia asociada a este producto',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar el queryset si es necesario
        self.fields['empresa'].queryset = EmpresaSocia.objects.all().order_by('nombre_empresa')

    def clean_precio_base(self):
        precio_base = self.cleaned_data.get('precio_base')
        if precio_base is not None:
            if precio_base <= 0:
                raise forms.ValidationError('El precio base debe ser mayor a 0.')
            if precio_base > 99999999.99:
                raise forms.ValidationError('El precio base no puede ser mayor a 99,999,999.99')
        return precio_base

    def clean_nombre_producto(self):
        nombre_producto = self.cleaned_data.get('nombre_producto')
        if nombre_producto:
            # Verificar si ya existe un producto con el mismo nombre (excluyendo el actual si es edición)
            queryset = Producto.objects.filter(nombre_producto__iexact=nombre_producto)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Ya existe un producto con este nombre.')
        
        return nombre_producto

class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = ['nombre_cliente', 'email', 'telefono', 'direccion']
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'placeholder': 'Ingrese el nombre completo del cliente'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'placeholder': 'cliente@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'placeholder': '+34 600 123 456'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'placeholder': 'Ingrese la dirección completa...',
                'rows': 3
            }),
        }
        labels = {
            'nombre_cliente': 'Nombre del Cliente',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
        }
        help_texts = {
            'nombre_cliente': 'Nombre completo del cliente',
            'email': 'Correo electrónico de contacto (opcional)',
            'telefono': 'Número de teléfono (opcional)',
            'direccion': 'Dirección completa (opcional)',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar si ya existe un cliente con el mismo email (excluyendo el actual si es edición)
            queryset = Cliente.objects.filter(email__iexact=email)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Ya existe un cliente con este email.')
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Validación básica del teléfono
            if len(telefono) < 5:
                raise forms.ValidationError('El número de teléfono parece demasiado corto.')
            
            # Verificar si ya existe un cliente con el mismo teléfono
            queryset = Cliente.objects.filter(telefono=telefono)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Ya existe un cliente con este número de teléfono.')
        
        return telefono

    def clean_nombre_cliente(self):
        nombre_cliente = self.cleaned_data.get('nombre_cliente')
        if nombre_cliente and len(nombre_cliente.strip()) < 2:
            raise forms.ValidationError('El nombre del cliente debe tener al menos 2 caracteres.')
        return nombre_cliente.strip()

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['producto', 'cliente', 'usuario', 'fecha_inicio', 'fecha_fin', 'estado', 'monto_venta']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'data-type': 'select'
            }),
            'cliente': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'data-type': 'select'
            }),
            'usuario': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'data-type': 'select'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'type': 'date',
                'min': '2020-01-01'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'type': 'date',
                'min': '2020-01-01'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'data-type': 'select'
            }),
            'monto_venta': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'producto': 'Producto',
            'cliente': 'Cliente',
            'usuario': 'Usuario Responsable',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Finalización',
            'estado': 'Estado de la Venta',
            'monto_venta': 'Monto de Venta',
        }
        help_texts = {
            'producto': 'Seleccione el producto vendido',
            'cliente': 'Seleccione el cliente',
            'usuario': 'Seleccione el usuario responsable de la venta',
            'fecha_inicio': 'Fecha en que inicia la venta/proyecto',
            'fecha_fin': 'Fecha estimada o real de finalización (opcional)',
            'estado': 'Estado actual del proceso de venta',
            'monto_venta': 'Monto total de la venta',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar los querysets de manera más legible
        self.fields['producto'].queryset = Producto.objects.all().select_related('empresa').order_by('nombre_producto')
        self.fields['cliente'].queryset = Cliente.objects.all().order_by('nombre_cliente')
        self.fields['usuario'].queryset = Usuario.objects.all().order_by('username')
        
        # Establecer fecha mínima para fecha_inicio (hoy)
        today = datetime.date.today()
        self.fields['fecha_inicio'].widget.attrs['min'] = today.isoformat()

    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        if fecha_inicio:
            if fecha_inicio < datetime.date(2020, 1, 1):
                raise forms.ValidationError('La fecha de inicio no puede ser anterior al año 2020.')
            if fecha_inicio > datetime.date.today() + datetime.timedelta(days=365):
                raise forms.ValidationError('La fecha de inicio no puede ser mayor a un año desde hoy.')
        return fecha_inicio

    def clean_fecha_fin(self):
        fecha_fin = self.cleaned_data.get('fecha_fin')
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        
        if fecha_fin and fecha_inicio:
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError('La fecha de fin no puede ser anterior a la fecha de inicio.')
            
            # Validar que la fecha fin no sea más de 2 años después de la fecha inicio
            max_fecha_fin = fecha_inicio + datetime.timedelta(days=730)  # 2 años
            if fecha_fin > max_fecha_fin:
                raise forms.ValidationError('La fecha de fin no puede ser mayor a 2 años después de la fecha de inicio.')
        
        return fecha_fin

    def clean_monto_venta(self):
        monto_venta = self.cleaned_data.get('monto_venta')
        if monto_venta is not None:
            if monto_venta <= 0:
                raise forms.ValidationError('El monto de venta debe ser mayor a 0.')
            if monto_venta > 9999999.99:
                raise forms.ValidationError('El monto de venta no puede ser mayor a 9,999,999.99')
        return monto_venta

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        fecha_fin = cleaned_data.get('fecha_fin')

        # Si el estado es "Finalizado", fecha_fin debe ser obligatoria
        if estado == 'Finalizado' and not fecha_fin:
            self.add_error('fecha_fin', 'La fecha de finalización es obligatoria cuando el estado es "Finalizado".')

        return cleaned_data

class ComisionForm(forms.ModelForm):
    class Meta:
        model = Comision
        fields = ['venta', 'regla', 'usuario', 'monto_comision', 'fecha_pagada', 'estado']
        widgets = {
            'venta': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'data-type': 'select'
            }),
            'regla': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'data-type': 'select'
            }),
            'usuario': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'data-type': 'select'
            }),
            'monto_comision': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'fecha_pagada': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'type': 'date'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 estado-selector',
                'data-type': 'select'
            }),
        }
        labels = {
            'venta': 'Venta Asociada',
            'regla': 'Regla de Comisión',
            'usuario': 'Usuario Beneficiario',
            'monto_comision': 'Monto de Comisión',
            'fecha_pagada': 'Fecha de Pago',
            'estado': 'Estado de Comisión',
        }
        help_texts = {
            'venta': 'Seleccione la venta asociada a esta comisión',
            'regla': 'Regla de comisión aplicada',
            'usuario': 'Usuario que recibe la comisión',
            'monto_comision': 'Monto calculado de la comisión',
            'fecha_pagada': 'Fecha en que se pagó la comisión (solo para estado "Pagada")',
            'estado': 'Estado actual de la comisión',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar los querysets
        self.fields['venta'].queryset = Venta.objects.all().select_related('cliente', 'producto').order_by('-fecha_creacion')
        self.fields['regla'].queryset = ReglaComision.objects.filter(activa=True).order_by('nombre_regla')
        self.fields['usuario'].queryset = Usuario.objects.all().order_by('username')
        
        # Si es una nueva comisión, establecer estado por defecto
        if not self.instance.pk:
            self.fields['estado'].initial = 'Pendiente'

    def clean_monto_comision(self):
        monto_comision = self.cleaned_data.get('monto_comision')
        if monto_comision is not None:
            if monto_comision <= 0:
                raise forms.ValidationError('El monto de comisión debe ser mayor a 0.')
            if monto_comision > 9999999.99:
                raise forms.ValidationError('El monto de comisión no puede ser mayor a 9,999,999.99')
        return monto_comision

    def clean_fecha_pagada(self):
        fecha_pagada = self.cleaned_data.get('fecha_pagada')
        estado = self.cleaned_data.get('estado')
        
        if estado == 'Pagada' and not fecha_pagada:
            raise forms.ValidationError('La fecha de pago es obligatoria cuando el estado es "Pagada".')
        
        if fecha_pagada and fecha_pagada > datetime.date.today():
            raise forms.ValidationError('La fecha de pago no puede ser futura.')
        
        return fecha_pagada

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        fecha_pagada = cleaned_data.get('fecha_pagada')
        
        # Validaciones cruzadas entre estado y fecha_pagada
        if estado == 'Pagada' and not fecha_pagada:
            self.add_error('fecha_pagada', 'Debe especificar una fecha de pago cuando el estado es "Pagada".')
        
        if estado != 'Pagada' and fecha_pagada:
            self.add_error('fecha_pagada', 'La fecha de pago solo debe especificarse cuando el estado es "Pagada".')
        
        # Validar que la venta y regla sean compatibles
        venta = cleaned_data.get('venta')
        regla = cleaned_data.get('regla')
        
        if venta and regla:
            # Verificar que el usuario de la comisión coincida con alguna relación
            usuario_comision = cleaned_data.get('usuario')
            if usuario_comision and venta.usuario != usuario_comision:
                # Podría ser una validación opcional dependiendo de las reglas de negocio
                pass
        
        return cleaned_data

class ReglaComisionForm(forms.ModelForm):
    # Campos adicionales para los criterios JSON
    monto_minimo = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0'
        }),
        help_text='Monto mínimo de venta para aplicar la regla (opcional)'
    )
    
    monto_maximo = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0'
        }),
        help_text='Monto máximo de venta para aplicar la regla (opcional)'
    )
    
    productos = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Producto.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
        }),
        help_text='Productos específicos para la regla (dejar vacío para todos)'
    )

    class Meta:
        model = ReglaComision
        fields = ['nombre_regla', 'usuario_director', 'comision_empresa', 'comision_usuario', 'activa']
        widgets = {
            'nombre_regla': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'placeholder': 'Ej: Regla Comisión Premium'
            }),
            'usuario_director': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200'
            }),
            'comision_empresa': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'comision_usuario': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
        }
        labels = {
            'nombre_regla': 'Nombre de la Regla',
            'usuario_director': 'Usuario Director',
            'comision_empresa': 'Comisión Empresa (%)',
            'comision_usuario': 'Comisión Usuario (%)',
            'activa': 'Regla Activa',
        }
        help_texts = {
            'nombre_regla': 'Nombre descriptivo para identificar la regla',
            'usuario_director': 'Usuario director asociado a esta regla',
            'comision_empresa': 'Porcentaje de comisión para la empresa (0-100%)',
            'comision_usuario': 'Porcentaje de comisión para el usuario (0-100%)',
            'activa': 'Indica si la regla está activa y se aplica a nuevas ventas',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar usuarios
        self.fields['usuario_director'].queryset = Usuario.objects.all().order_by('username')
        
        # Si es una edición, cargar los valores existentes de criterios
        if self.instance and self.instance.pk and self.instance.criterios:
            criterios = self.instance.criterios
            self.fields['monto_minimo'].initial = criterios.get('monto_minimo')
            self.fields['monto_maximo'].initial = criterios.get('monto_maximo')
            if 'productos' in criterios:
                self.fields['productos'].initial = Producto.objects.filter(pk__in=criterios['productos'])

    def clean_comision_empresa(self):
        comision = self.cleaned_data.get('comision_empresa')
        if comision is not None:
            if comision < 0:
                raise forms.ValidationError('La comisión de la empresa no puede ser negativa.')
            if comision > 100:
                raise forms.ValidationError('La comisión de la empresa no puede ser mayor al 100%.')
        return comision

    def clean_comision_usuario(self):
        comision = self.cleaned_data.get('comision_usuario')
        if comision is not None:
            if comision < 0:
                raise forms.ValidationError('La comisión del usuario no puede ser negativa.')
            if comision > 100:
                raise forms.ValidationError('La comisión del usuario no puede ser mayor al 100%.')
        return comision

    def clean_monto_maximo(self):
        monto_minimo = self.cleaned_data.get('monto_minimo')
        monto_maximo = self.cleaned_data.get('monto_maximo')
        
        if monto_minimo and monto_maximo:
            if monto_maximo <= monto_minimo:
                raise forms.ValidationError('El monto máximo debe ser mayor al monto mínimo.')
        
        return monto_maximo

    def clean(self):
        cleaned_data = super().clean()
        comision_empresa = cleaned_data.get('comision_empresa')
        comision_usuario = cleaned_data.get('comision_usuario')
        
        # Validar que la suma de comisiones no exceda el 100%
        if comision_empresa and comision_usuario:
            total_comisiones = comision_empresa + comision_usuario
            if total_comisiones > 100:
                self.add_error('comision_empresa', f'La suma total de comisiones ({total_comisiones}%) no puede exceder el 100%.')
                self.add_error('comision_usuario', f'La suma total de comisiones ({total_comisiones}%) no puede exceder el 100%.')
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Construir el objeto JSON de criterios
        criterios = {}
        
        monto_minimo = self.cleaned_data.get('monto_minimo')
        monto_maximo = self.cleaned_data.get('monto_maximo')
        productos = self.cleaned_data.get('productos')
        
        if monto_minimo:
            criterios['monto_minimo'] = float(monto_minimo)
        if monto_maximo:
            criterios['monto_maximo'] = float(monto_maximo)
        if productos:
            criterios['productos'] = [producto.pk for producto in productos]
        
        instance.criterios = criterios
        
        if commit:
            instance.save()
        
        return instance