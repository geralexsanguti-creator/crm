from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name="home"),    
    path('', include('django.contrib.auth.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('productos/', views.productos, name='productos'),   
    
    path('producto/agregar/', views.crear_producto, name='agregar_producto'),
    path('producto/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('producto/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('login/',views.login_view, name='login'),
    path('logout/',views.logout_view, name='logout'),
    path('ventas/', views.ventas, name='ventas'),
    path('clientes/', views.clientes, name='clientes'),

    path('producto/<int:producto_id>/', views.obtener_producto, name='obtener_producto'),  # NUEVA
    path('producto/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('producto/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('producto/<int:producto_id>/precio/', views.obtener_precio_producto, name='obtener_precio_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('productos/obtener/<int:producto_id>/', views.obtener_datos_producto, name='obtener_producto'),
    path('productos/detalle/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

    # URLs para clientes
    path('clientes/', views.clientes, name='clientes'),
    path('cliente/agregar/', views.agregar_cliente, name='agregar_cliente'),
    path('cliente/<int:cliente_id>/', views.obtener_cliente, name='obtener_cliente'),
    path('cliente/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('cliente/<int:cliente_id>/eliminar/', views.eliminar_cliente, name='eliminar_cliente'),

    # URLs para ventas
    path('ventas/', views.ventas, name='ventas'),
    path('venta/agregar/', views.agregar_venta, name='agregar_venta'),
    path('venta/<int:venta_id>/', views.obtener_venta, name='obtener_venta'),
    path('venta/<int:venta_id>/editar/', views.editar_venta, name='editar_venta'),
    path('venta/<int:venta_id>/eliminar/', views.eliminar_venta, name='eliminar_venta'),
    path('venta/<int:venta_id>/cambiar-estado/', views.cambiar_estado_venta, name='cambiar_estado_venta'),
   
]