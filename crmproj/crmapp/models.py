from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

# Create your models here.

class Usuario(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)

    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Role(models.Model):
    PERMISSION_CHOISES = [
        (0, 'No tiene accesso'),
        (1, 'Ver Solo'),
        (2, 'Crear y Modificar'),
    ]
    
    role_name = models.CharField(max_length=150, primary_key=True)
    productos = models.IntegerField(choices=PERMISSION_CHOISES, default=0)
    ventas = models.IntegerField(choices=PERMISSION_CHOISES, default=0)
    clientes = models.IntegerField(choices=PERMISSION_CHOISES, default=0)
    empresas = models.IntegerField(choices=PERMISSION_CHOISES, default=0)
    comisiones = models.IntegerField(choices=PERMISSION_CHOISES, default=0)
    regla_comisiones = models.IntegerField(choices=PERMISSION_CHOISES, default=0)
    equipos = models.IntegerField(choices=PERMISSION_CHOISES, default=0)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.role_name
    

class UserRole(models.Model):
    user_id = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_roles'
        verbose_name = 'user_role'
        verbose_name_plural = 'user_roles'
        unique_together = ('user_id', 'role')
    
    def __str__(self):
        return f"{self.user_id.username}-{self.role.role_name}"
    

class EmpresaSocia(models.Model):
    empresa_id = models.AutoField(primary_key=True)
    nombre_empresa = models.CharField(max_length=150, unique=True)
    comision_aplicable = models.DecimalField(max_digits=5, decimal_places=2)
    contacto_email = models.EmailField()
    telefono = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_empresa

class Producto(models.Model):
    producto_id = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    empresa = models.ForeignKey(EmpresaSocia, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_producto

class Cliente(models.Model):
    cliente_id = models.AutoField(primary_key=True)
    nombre_cliente = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_cliente
    

class Venta(models.Model):
    ESTADO_CHOICES = [
        ('Prospecto', 'Prospecto'),
        ('Contratado', 'Contratado'),
        ('En Instalación', 'En Instalación'),
        ('Finalizado', 'Finalizado'),
        ('Cancelado', 'Cancelado'),
    ]

    venta_id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    monto_venta = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta {self.venta_id} - {self.cliente.nombre_cliente}"


class ReglaComision(models.Model):
    regla_id = models.AutoField(primary_key=True)
    nombre_regla = models.CharField(max_length=100)
    usuario_director = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    criterios = models.JSONField()
    comision_empresa = models.DecimalField(max_digits=5, decimal_places=2)
    comision_usuario = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_regla


class Comision(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Pagada', 'Pagada'),
        ('Cancelada', 'Cancelada'),
    ]

    comision_id = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    regla = models.ForeignKey(ReglaComision, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    monto_comision = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_calculada = models.DateTimeField(auto_now_add=True)
    fecha_pagada = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')

    def __str__(self):
        return f"Comisión {self.comision_id} - {self.usuario}"


class Equipo(models.Model):
    equipo_id = models.AutoField(primary_key=True)
    nombre_equipo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_equipo


