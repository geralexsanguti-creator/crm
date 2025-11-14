from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import json
from django.utils.safestring import mark_safe
from .forms import ProductoForm, LoginForm, VentaForm, ClienteForm, EmpresaSociaForm , EquipoForm, ReglaComisionForm, ComisionForm
from django.http import JsonResponse
from django.contrib import messages
from .models import Producto, Venta, UserRole, Cliente, Equipo, EmpresaSocia, ReglaComision, Comision
from django.db.models import Sum, F, Avg, Max, Min
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def home(request):
    return render(request, 'home.html')

#Methodos para rl modelo equipos
def crear_equipo(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_equipos')  # Redirige a donde necesites
    else:
        form = EquipoForm()
    
    return render(request, 'crear_equipo.html', {'form': form})

def editar_equipo(request, equipo_id):
    equipo = Equipo.objects.get(pk=equipo_id)
    if request.method == 'POST':
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            return redirect('lista_equipos')
    else:
        form = EquipoForm(instance=equipo)
    
    return render(request, 'editar_equipo.html', {'form': form})

#Methodos para rl modelo empresa
def crear_empresa_socia(request):
    if request.method == 'POST':
        form = EmpresaSociaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_empresas')  # Redirige a donde necesites
    else:
        form = EmpresaSociaForm()
    
    return render(request, 'empresas/crear_empresa.html', {'form': form})

def editar_empresa_socia(request, empresa_id):
    empresa = get_object_or_404(EmpresaSocia, pk=empresa_id)
    if request.method == 'POST':
        form = EmpresaSociaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            return redirect('lista_empresas')
    else:
        form = EmpresaSociaForm(instance=empresa)
    
    return render(request, 'empresas/editar_empresa.html', {'form': form})

#Methodos para rl modelo producto
def productos(request):
    # Solo productos no eliminados
    productos_list = Producto.objects.filter(eliminado=False)
    
    # Estadísticas (solo productos no eliminados)
    total_productos = productos_list.count()
    productos_activos = productos_list.filter(activo=True).count()
    cantidad_bajo = productos_list.filter(cantidad__lt=5).count()
    valor_total = sum(producto.precio * producto.cantidad for producto in productos_list)
    
    context = {
        'productos': productos_list,
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'cantidad_bajo': cantidad_bajo,
        'valor_total': valor_total,
    }
    return render(request, 'dashboard/productos.html', context)

def eliminar_producto(request, producto_id):
    try:
        # Buscar producto que no esté eliminado
        producto = get_object_or_404(Producto, id=producto_id, eliminado=False)
        nombre_producto = producto.nombre
        
        # Eliminación suave
        producto.eliminado = True
        producto.fecha_eliminacion = timezone.now()
        producto.activo = False
        producto.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Producto "{nombre_producto}" eliminado correctamente'
        })
        
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'El producto no existe o ya fue eliminado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar el producto: {str(e)}'
        })

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    
    return render(request, 'productos/crear_producto.html', {'form': form})

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'productos/editar_producto.html', {'form': form})

@require_http_methods(["GET"])
def obtener_datos_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        
        datos_producto = {
            'id': producto.id,
            'nombre': producto.nombre,
            'codigo': producto.codigo or '',
            'descripcion': producto.descripcion or '',
            'precio': str(producto.precio),
            'cantidad': producto.cantidad,
            'categoria': producto.categoria.id if producto.categoria else '',
            'activo': producto.activo,
            'imagen_url': producto.imagen.url if producto.imagen else '',
        }
        
        return JsonResponse(datos_producto)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener datos del producto: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def obtener_precio_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        return JsonResponse({
            'precio': str(producto.precio),
            'stock': producto.cantidad
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener precio del producto: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def obtener_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        
        datos_producto = {
            'id': producto.id,
            'nombre': producto.nombre,
            'codigo': producto.codigo or '',
            'descripcion': producto.descripcion or '',
            'precio': str(producto.precio),
            'cantidad': producto.cantidad,
            'cantidad_minima': producto.cantidad_minima,
            'categoria': producto.categoria.id if producto.categoria else '',
            'activo': producto.activo,
        }
        
        # Manejar la imagen
        if producto.imagen:
            datos_producto['imagen_url'] = request.build_absolute_uri(producto.imagen.url)
        else:
            datos_producto['imagen_url'] = ''
        
        return JsonResponse(datos_producto)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener datos del producto: {str(e)}'
        }, status=500)

def eliminar_producto(request, producto_id):
    try:
        # Buscar producto que no esté eliminado
        producto = get_object_or_404(Producto, id=producto_id, eliminado=False)
        nombre_producto = producto.nombre
        
        # Eliminación suave
        producto.eliminado = True
        producto.fecha_eliminacion = timezone.now()
        producto.activo = False
        producto.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Producto "{nombre_producto}" eliminado correctamente'
        })
        
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'El producto no existe o ya fue eliminado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar el producto: {str(e)}'
        })
    
@require_http_methods(["POST"])
def restaurar_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id, eliminado=True)
        producto.eliminado = False
        producto.fecha_eliminacion = None
        producto.activo = True
        producto.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Producto "{producto.nombre}" restaurado correctamente'
        })
        
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Producto no encontrado'
        })

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'productos/detalle.html', {'producto': producto})
#method para modelo usuarios y dashboard

@login_required
def dashboard(request):
    user_roles = UserRole.objects.filter(user_id=request.user.user_id)
    permissions = {
        'clientes': 0,
        'ventas': 0,
        'productos': 0,
        'categorias': 0,    
    }

    for user_role in user_roles:
        role = user_role.role
        for module in permissions.keys():
            current_permission = getattr(role,module)
            if current_permission > permissions[module]:
                permissions[module] = current_permission

    context = {
        'usuario': request.user,
        'permissions': permissions,
        'roles':  { ur.role.role_name for ur in user_roles}
    }
    return render(request, 'dashboard/dashboard.html', context)

def usuarios(request):
    try:
        # Tu lógica actual para guardar el producto
        nombre = request.POST.get('nombre')
        codigo = request.POST.get('codigo')
        precio = request.POST.get('precio')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        categoria_id = request.POST.get('categoria')
        activo = request.POST.get('activo') == 'on'
        
        # Validaciones básicas
        if not nombre or not precio:
            return JsonResponse({
                'success': False,
                'message': 'Nombre y precio son campos obligatorios'
            })
        
        # Crear y guardar el producto
        producto = Producto(
            nombre=nombre,
            codigo=codigo,
            precio=precio,
            cantidad=cantidad,
            categoria_id=categoria_id,
            descripcion=descripcion,
            activo=activo
        )
        
        # Manejar la imagen si se subió
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']
        
        producto.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Producto guardado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al guardar el producto: {str(e)}'
        })

    try:
        venta = get_object_or_404(Venta, id=venta_id)
        nuevo_estado = request.POST.get('estado')
        
        if nuevo_estado not in dict(Venta.EstadoVenta.choices):
            return JsonResponse({
                'success': False,
                'message': 'Estado no válido'
            })
        
        estado_anterior = venta.estado
        venta.estado = nuevo_estado
        venta.save()
        
        # Manejar cambios de stock
        if venta.producto:
            if estado_anterior != Venta.EstadoVenta.CERRADO and nuevo_estado == Venta.EstadoVenta.CERRADO:
                # Cerrar venta: restar stock
                venta.producto.cantidad -= venta.cantidad
                venta.producto.save()
            elif estado_anterior == Venta.EstadoVenta.CERRADO and nuevo_estado != Venta.EstadoVenta.CERRADO:
                # Reabrir venta: restaurar stock
                venta.producto.cantidad += venta.cantidad
                venta.producto.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Estado de venta #{venta.id} cambiado a {venta.get_estado_display()}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al cambiar estado: {str(e)}'
        })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request.user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Usuario o Contraseña Incorrecto')

    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

#method para modelo reglas de comision
def crear_regla_comision(request):
    if request.method == 'POST':
        form = ReglaComisionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_reglas_comision')
    else:
        form = ReglaComisionForm()
    
    return render(request, 'reglas/crear_regla_comision.html', {'form': form})

def editar_regla_comision(request, regla_id):

    regla = get_object_or_404(ReglaComision, pk=regla_id)
    if request.method == 'POST':
        form = ReglaComisionForm(request.POST, instance=regla)
        if form.is_valid():
            form.save()
            return redirect('lista_reglas_comision')
    else:
        form = ReglaComisionForm(instance=regla)
    
    return render(request, 'reglas/editar_regla_comision.html', {'form': form})

def crear_comision(request):
    if request.method == 'POST':
        form = ComisionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_comisiones')
    else:
        form = ComisionForm()
    
    return render(request, 'comisiones/crear_comision.html', {'form': form})

def editar_comision(request, comision_id):
    comision = get_object_or_404(Comision, pk=comision_id)
    if request.method == 'POST':
        form = ComisionForm(request.POST, instance=comision)
        if form.is_valid():
            form.save()
            return redirect('lista_comisiones')
    else:
        form = ComisionForm(instance=comision)
    
    return render(request, 'comisiones/editar_comision.html', {'form': form})

    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request.user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Usuario o Contraseña Incorrecto')

    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

#method para modelo ventas
@require_http_methods(["POST"])
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Usted salio del Sistema Exitosamente')
    return redirect('login')

def crear_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save()
            messages.success(request, f'Venta #{venta.id} creada exitosamente.')
            return redirect('detalle_venta', pk=venta.id)
    else:
        form = VentaForm()
    
    return render(request, 'ventas/venta_form.html', {'form': form})

def ventas(request):
    # Obtener parámetros de búsqueda y filtros
    query = request.GET.get('q', '')
    estado_filter = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    ventas_list = Venta.objects.all()
    
    # Aplicar filtros
    if query:
        ventas_list = ventas_list.filter(
            Q(cliente__nombre__icontains=query) |
            Q(producto__nombre__icontains=query) |
            Q(notas__icontains=query)
        )
    
    if estado_filter:
        ventas_list = ventas_list.filter(estado=estado_filter)
    
    if fecha_inicio:
        ventas_list = ventas_list.filter(creado_en__date__gte=fecha_inicio)
    
    if fecha_fin:
        ventas_list = ventas_list.filter(creado_en__date__lte=fecha_fin)
    
    # Estadísticas
    total_ventas = ventas_list.count()
    ventas_activas = ventas_list.exclude(
        estado__in=[Venta.EstadoVenta.CERRADO, Venta.EstadoVenta.CANCELADO]
    ).count()
    total_monto = ventas_list.aggregate(Sum('monto'))['monto__sum'] or 0
    ventas_este_mes = Venta.objects.filter(
        creado_en__month=datetime.now().month,
        creado_en__year=datetime.now().year
    ).count()
    
    # Ventas por estado
    ventas_por_estado = ventas_list.values('estado').annotate(
        total=Count('id'),
        monto_total=Sum('monto')
    )
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(ventas_list, 10)  # 10 ventas por página
    
    try:
        ventas_paginados = paginator.page(page)
    except PageNotAnInteger:
        ventas_paginados = paginator.page(1)
    except EmptyPage:
        ventas_paginados = paginator.page(paginator.num_pages)
    
    context = {
        'ventas': ventas_paginados,
        'total_ventas': total_ventas,
        'ventas_activas': ventas_activas,
        'total_monto': total_monto,
        'ventas_este_mes': ventas_este_mes,
        'ventas_por_estado': ventas_por_estado,
        'estados_venta': Venta.EstadoVenta.choices,
        'clientes': Cliente.objects.all(),
        'productos': Producto.objects.filter(activo=True, cantidad__gt=0),
    }
    return render(request, 'dashboard/ventas.html', context)

def crear_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_ventas')
    else:
        form = VentaForm()
    
    return render(request, 'ventas/crear_venta.html', {'form': form})

def editar_venta(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id)
    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        if form.is_valid():
            form.save()
            return redirect('lista_ventas')
    else:
        form = VentaForm(instance=venta)
    
    return render(request, 'ventas/editar_venta.html', {'form': form})
    
@require_http_methods(["POST"])
def editar_venta(request, venta_id):
    try:
        venta = get_object_or_404(Venta, id=venta_id)
        
        if not venta.puede_editarse:
            return JsonResponse({
                'success': False,
                'message': 'No se puede editar una venta cerrada o cancelada'
            })
        
        # Guardar valores anteriores para actualizar stock
        cantidad_anterior = venta.cantidad
        estado_anterior = venta.estado
        producto_anterior = venta.producto
        
        form = VentaForm(request.POST, instance=venta)
        
        if form.is_valid():
            venta = form.save()
            
            # Manejar actualización de stock
            if venta.producto:
                if estado_anterior != Venta.EstadoVenta.CERRADO and venta.estado == Venta.EstadoVenta.CERRADO:
                    # Si se cierra la venta, restar stock
                    venta.producto.cantidad -= venta.cantidad
                    venta.producto.save()
                elif estado_anterior == Venta.EstadoVenta.CERRADO and venta.estado != Venta.EstadoVenta.CERRADO:
                    # Si se reabre una venta cerrada, restaurar stock
                    venta.producto.cantidad += cantidad_anterior
                    venta.producto.save()
                elif venta.estado == Venta.EstadoVenta.CERRADO and (cantidad_anterior != venta.cantidad or producto_anterior != venta.producto):
                    # Si cambia la cantidad o producto en una venta cerrada, ajustar stock
                    if producto_anterior:
                        producto_anterior.cantidad += cantidad_anterior
                        producto_anterior.save()
                    venta.producto.cantidad -= venta.cantidad
                    venta.producto.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Venta #{venta.id} actualizada correctamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al actualizar venta: {str(e)}'
        })

@require_http_methods(["POST"])
def eliminar_venta(request, venta_id):
    try:
        venta = get_object_or_404(Venta, id=venta_id)
        
        if not venta.puede_editarse:
            return JsonResponse({
                'success': False,
                'message': 'No se puede eliminar una venta cerrada o cancelada'
            })
        
        # Restaurar stock si la venta estaba cerrada
        if venta.estado == Venta.EstadoVenta.CERRADO and venta.producto:
            venta.producto.cantidad += venta.cantidad
            venta.producto.save()
        
        venta_id = venta.id
        venta.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Venta #{venta_id} eliminada correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar venta: {str(e)}'
        })

@require_http_methods(["POST"])
def agregar_venta(request):
    try:
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save()
            
            # Actualizar stock del producto si la venta se cierra
            if venta.estado == Venta.EstadoVenta.CERRADO and venta.producto:
                venta.producto.cantidad -= venta.cantidad
                venta.producto.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Venta #{venta.id} agregada correctamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al agregar venta: {str(e)}'
        })

@require_http_methods(["POST"])
def editar_venta(request, venta_id):
    try:
        venta = get_object_or_404(Venta, id=venta_id)
        
        if not venta.puede_editarse:
            return JsonResponse({
                'success': False,
                'message': 'No se puede editar una venta cerrada o cancelada'
            })
        
        # Guardar valores anteriores para actualizar stock
        cantidad_anterior = venta.cantidad
        estado_anterior = venta.estado
        producto_anterior = venta.producto
        
        form = VentaForm(request.POST, instance=venta)
        
        if form.is_valid():
            venta = form.save()
            
            # Manejar actualización de stock
            if venta.producto:
                if estado_anterior != Venta.EstadoVenta.CERRADO and venta.estado == Venta.EstadoVenta.CERRADO:
                    # Si se cierra la venta, restar stock
                    venta.producto.cantidad -= venta.cantidad
                    venta.producto.save()
                elif estado_anterior == Venta.EstadoVenta.CERRADO and venta.estado != Venta.EstadoVenta.CERRADO:
                    # Si se reabre una venta cerrada, restaurar stock
                    venta.producto.cantidad += cantidad_anterior
                    venta.producto.save()
                elif venta.estado == Venta.EstadoVenta.CERRADO and (cantidad_anterior != venta.cantidad or producto_anterior != venta.producto):
                    # Si cambia la cantidad o producto en una venta cerrada, ajustar stock
                    if producto_anterior:
                        producto_anterior.cantidad += cantidad_anterior
                        producto_anterior.save()
                    venta.producto.cantidad -= venta.cantidad
                    venta.producto.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Venta #{venta.id} actualizada correctamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al actualizar venta: {str(e)}'
        })

@require_http_methods(["POST"])
def eliminar_venta(request, venta_id):
    try:
        venta = get_object_or_404(Venta, id=venta_id)
        
        if not venta.puede_editarse:
            return JsonResponse({
                'success': False,
                'message': 'No se puede eliminar una venta cerrada o cancelada'
            })
        
        # Restaurar stock si la venta estaba cerrada
        if venta.estado == Venta.EstadoVenta.CERRADO and venta.producto:
            venta.producto.cantidad += venta.cantidad
            venta.producto.save()
        
        venta_id = venta.id
        venta.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Venta #{venta_id} eliminada correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar venta: {str(e)}'
        })

@require_http_methods(["GET"])
def obtener_venta(request, venta_id):
    try:
        venta = get_object_or_404(Venta, id=venta_id)
        
        datos_venta = {
            'id': venta.id,
            'cliente': venta.cliente.id,
            'producto': venta.producto.id if venta.producto else '',
            'cantidad': venta.cantidad,
            'precio_unitario': str(venta.precio_unitario) if venta.precio_unitario else '',
            'monto': str(venta.monto),
            'estado': venta.estado,
            'notas': venta.notas or '',
            'puede_editarse': venta.puede_editarse,
        }
        
        return JsonResponse(datos_venta)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener datos de la venta: {str(e)}'
        }, status=500)

@require_http_methods(["POST"])
def cambiar_estado_venta(request, venta_id):
     try:
        venta = get_object_or_404(Venta, id=venta_id)
        
        datos_venta = {
            'id': venta.id,
            'cliente': venta.cliente.id,
            'producto': venta.producto.id if venta.producto else '',
            'cantidad': venta.cantidad,
            'precio_unitario': str(venta.precio_unitario) if venta.precio_unitario else '',
            'monto': str(venta.monto),
            'estado': venta.estado,
            'notas': venta.notas or '',
            'puede_editarse': venta.puede_editarse,
        }
        
        return JsonResponse(datos_venta)
        
     except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener datos de la venta: {str(e)}'
        }, status=500)


#method para modelo clientes
@login_required
def clientes(request):
    # Obtener parámetros de búsqueda
    query = request.GET.get('q', '')
    
    if query:
        clientes_list = Cliente.objects.filter(nombre__icontains=query)
    else:
        clientes_list = Cliente.objects.all()
    
    # Estadísticas
    total_clientes = clientes_list.count()
    clientes_nuevos = clientes_list.filter(tipo='nuevo').count()
    clientes_recurrentes = clientes_list.filter(tipo='recurrente').count()
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(clientes_list, 10)  # 10 clientes por página
    
    try:
        clientes_paginados = paginator.page(page)
    except PageNotAnInteger:
        clientes_paginados = paginator.page(1)
    except EmptyPage:
        clientes_paginados = paginator.page(paginator.num_pages)
    
    context = {
        'clientes': clientes_paginados,
        'total_clientes': total_clientes,
        'clientes_nuevos': clientes_nuevos,
        'clientes_recurrentes': clientes_recurrentes,
    }
    return render(request, 'dashboard/clientes.html', context)

def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    
    return render(request, 'clientes/crear_cliente.html', {'form': form})

def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'clientes/editar_cliente.html', {'form': form})

@require_http_methods(["GET"])
def obtener_cliente(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        
        datos_cliente = {
            'id': cliente.id,
            'nombre': cliente.nombre,
            'email': cliente.email or '',
            'telefono': cliente.telefono or '',
            'direccion': cliente.direccion or '',
            'tipo': cliente.tipo,
            'tipo_contrato': cliente.tipo_contrato or '',
            'tasa_comision': str(cliente.tasa_comision),
        }
        
        return JsonResponse(datos_cliente)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener datos del cliente: {str(e)}'
        }, status=500)

@require_http_methods(["POST"])
def agregar_cliente(request):
    try:
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Cliente "{cliente.nombre}" agregado correctamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al agregar cliente: {str(e)}'
        })

@require_http_methods(["POST"])
def editar_cliente(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        form = ClienteForm(request.POST, instance=cliente)
        
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Cliente "{cliente.nombre}" actualizado correctamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al actualizar cliente: {str(e)}'
        })

@require_http_methods(["POST"])
def eliminar_cliente(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        nombre_cliente = cliente.nombre
        
        # Verificar si el cliente tiene ventas asociadas (opcional)
        # if cliente.ventas.exists():
        #     return JsonResponse({
        #         'success': False,
        #         'message': 'No se puede eliminar el cliente porque tiene ventas asociadas'
        #     })
        
        cliente.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Cliente "{nombre_cliente}" eliminado correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar cliente: {str(e)}'
        })
    

@login_required
def clientes(request):
    # Obtener parámetros de búsqueda
    query = request.GET.get('q', '')
    
    if query:
        clientes_list = Cliente.objects.filter(nombre__icontains=query)
    else:
        clientes_list = Cliente.objects.all()
    
    # Estadísticas
    total_clientes = clientes_list.count()
    clientes_nuevos = clientes_list.filter(tipo='nuevo').count()
    clientes_recurrentes = clientes_list.filter(tipo='recurrente').count()
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(clientes_list, 10)  # 10 clientes por página
    
    try:
        clientes_paginados = paginator.page(page)
    except PageNotAnInteger:
        clientes_paginados = paginator.page(1)
    except EmptyPage:
        clientes_paginados = paginator.page(paginator.num_pages)
    
    context = {
        'clientes': clientes_paginados,
        'total_clientes': total_clientes,
        'clientes_nuevos': clientes_nuevos,
        'clientes_recurrentes': clientes_recurrentes,
    }
    return render(request, 'dashboard/clientes.html', context)

@require_http_methods(["GET"])
def obtener_cliente(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        
        datos_cliente = {
            'id': cliente.id,
            'nombre': cliente.nombre,
            'email': cliente.email or '',
            'telefono': cliente.telefono or '',
            'direccion': cliente.direccion or '',
            'tipo': cliente.tipo,
            'tipo_contrato': cliente.tipo_contrato or '',
            'tasa_comision': str(cliente.tasa_comision),
        }
        
        return JsonResponse(datos_cliente)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener datos del cliente: {str(e)}'
        }, status=500)

@require_http_methods(["POST"])
def agregar_cliente(request):
    try:
        form = ClientesForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Cliente "{cliente.nombre}" agregado correctamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al agregar cliente: {str(e)}'
        })

@require_http_methods(["POST"])
def editar_cliente(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        form = ClientesForm(request.POST, instance=cliente)
        
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Cliente "{cliente.nombre}" actualizado correctamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al actualizar cliente: {str(e)}'
        })

@require_http_methods(["POST"])
def eliminar_cliente(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        nombre_cliente = cliente.nombre
        
        # Verificar si el cliente tiene ventas asociadas (opcional)
        # if cliente.ventas.exists():
        #     return JsonResponse({
        #         'success': False,
        #         'message': 'No se puede eliminar el cliente porque tiene ventas asociadas'
        #     })
        
        cliente.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Cliente "{nombre_cliente}" eliminado correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar cliente: {str(e)}'
        })
