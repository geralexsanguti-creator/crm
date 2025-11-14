from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cliente, Usuario, UserRole, Role

@admin.register(Usuario)
class CustomUsuarioAdmin(UserAdmin):
    list_display = ('username', 'email',  'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email',  'first_name', 'last_name')
    ordering = ('-date_joined',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'clientes', 'ventas', 'productos', 'comisiones', 'regla_comisiones','equipos')
    list_filter = ('clientes', 'ventas', 'productos', 'comisiones')
    search_fields = ('role_name',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'role')
    list_filter = ('role',)
    search_fields = ('user_id__username', 'role__role_name')