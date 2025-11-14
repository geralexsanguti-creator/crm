from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name="home"),   
    path('dashboard/', views.dashboard, name='dashboard'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/crear/', views.crear_cliente, name='crear_cliente'),
    path('clientes/editar/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/', views.eliminar_cliente, name='eliminar_cliente'),
    path('clientes/<int:cliente_id>/datos/', views.obtener_datos_cliente, name='obtener_datos_cliente'),
    #urls productos
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('productos/editar/', views.editar_producto, name='editar_producto'),  # Sin ID
    path('productos/eliminar/', views.eliminar_producto, name='eliminar_producto'),  # Sin ID
    #path('productos/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    #path('productos/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    #  URL para empresas ...
    path('empresas/', views.lista_empresas, name='lista_empresas'),
    path('empresas/crear/', views.crear_empresa, name='crear_empresa'),
    path('empresas/editar/', views.editar_empresa, name='editar_empresa'),
    path('empresas/<int:empresa_id>/datos/', views.obtener_datos_empresa, name='obtener_datos_empresa'),
    path('empresas/eliminar/', views.eliminar_empresa, name='eliminar_empresa'),
    
    #  URL para ventas ...
    path('ventas/', views.lista_ventas, name='lista_ventas'),
    path('ventas/crear/', views.crear_venta, name='crear_venta'),
    path('ventas/editar/', views.editar_venta, name='editar_venta'),
    path('ventas/eliminar/', views.eliminar_venta, name='eliminar_venta'),
    #path('ventas/<int:venta_id>/editar/', views.editar_venta, name='editar_venta'),
    #path('ventas/<int:venta_id>/eliminar/', views.eliminar_venta, name='eliminar_venta'),


    path('equipos/', views.lista_equipos, name='lista_equipos'),
    path('equipos/agregar/', views.agregar_equipo, name='agregar_equipo'),
    path('equipos/editar/<int:equipo_id>/', views.editar_equipo, name='editar_equipo'),
    path('equipos/eliminar/<int:equipo_id>/', views.eliminar_equipo, name='eliminar_equipo'),
    path('equipos/detalle/<int:equipo_id>/', views.detalle_equipo, name='detalle_equipo'),
    path('equipos/dashboard/', views.dashboard_equipos, name='dashboard_equipos'),

    path('reglas_comisiones/', views.lista_reglas_comisiones, name='lista_reglas_comisiones'),
    
    path('comisiones/', views.lista_comisiones, name='lista_comisiones'),
    path('comisiones/agregar/', views.agregar_comision, name='agregar_comision'),
    path('comisiones/editar/<int:comision_id>/', views.editar_comision, name='editar_comision'),
    path('comisiones/eliminar/<int:comision_id>/', views.eliminar_comision, name='eliminar_comision'),
    #path('comisiones/marcar-pagada/<int:comision_id>/', views.marcar_como_pagada, name='marcar_como_pagada'),
    #path('comisiones/dashboard/', views.dashboard_comisiones, name='dashboard_comisiones'),
    #path('marcar-pagada/<int:comision_id>/', views.marcar_como_pagada, name='marcar_como_pagada'),
    #path('dashboard/', views.dashboard_comisiones, name='dashboard_comisiones'),

    path('crear-usuario/', views.crear_usuario, name='crear_usuario'),
    path('crear-rol/', views.crear_rol, name='crear_rol'),
    path('asignar-rol/', views.asignar_rol, name='asignar_rol'),


    
    path('login/',views.login_view, name='login'),
    path('logout/',views.logout_view, name='logout'),

]