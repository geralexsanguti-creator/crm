from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from .forms import ComisionForm, LoginForm, ProductoForm, EmpresaSociaForm, VentaForm, ClienteForm, EquipoForm, UsuarioForm, RoleForm
from django.http import JsonResponse
from django.contrib import messages
from .models import Producto, Usuario, Venta, Role, UserRole, Cliente, Equipo, EmpresaSocia, ReglaComision, Comision
from django.db.models import Sum, F, Avg, Max, Min, Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, date

# Create your views here.
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
                login(request, user)
                messages.success(request, f'Bienvenido {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Usuario o Contraseña Incorrecto')

    else:
        form = LoginForm()
    
    return render(request, 'registrations/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Usted salio del Sistema Exitosamente')
    return redirect('login')


def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    user_roles = UserRole.objects.filter(user_id=request.user.user_id)
    permissions = {
        'clientes': 0,
        'ventas': 0,
        'productos': 0,
        'empresas': 0, 
        'comisiones': 0,
        'regla_comisiones': 0,
        'equipos': 0,
           
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



#Modulo Productos CRUD
@login_required
def lista_productos(request):
    # Filtros
    empresa_id = request.GET.get('empresa', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    
    productos = Producto.objects.select_related('empresa').all()
    
    # Aplicar filtros
    if empresa_id:
        productos = productos.filter(empresa_id=empresa_id)
    
    if precio_min:
        try:
            productos = productos.filter(precio_base__gte=float(precio_min))
        except ValueError:
            pass
    
    if precio_max:
        try:
            productos = productos.filter(precio_base__lte=float(precio_max))
        except ValueError:
            pass
    
    # Estadísticas
    total_productos = productos.count()
    
    if productos.exists():
        precio_promedio = productos.aggregate(avg=Avg('precio_base'))['avg']
        precio_promedio = round(precio_promedio, 2)
    else:
        precio_promedio = 0
    
    total_empresas = EmpresaSocia.objects.count()
    
    # Productos agregados hoy
    hoy = timezone.now().date()
    productos_hoy = productos.filter(fecha_creacion__date=hoy).count()
    
    # Contar ventas por producto
    productos = productos.annotate(
        ventas_count=Count('venta')
    )
    
    # Paginación
    paginator = Paginator(productos.order_by('-fecha_creacion'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # FORMULARIO Y CONTEXTO
    form = ProductoForm()  # ← AGREGAR ESTO
    
    context = {
        'productos': page_obj,
        'total_productos': total_productos,
        'precio_promedio': precio_promedio,
        'total_empresas': total_empresas,
        'productos_hoy': productos_hoy,
        'empresas': EmpresaSocia.objects.all(),
        'form': form,  # ← AGREGAR ESTO
    }

    return render(request, 'tables/productos-list.html', context)  # ← NO OLVIDES EL CONTEXT

@login_required
def detalle_producto(request, producto_id):
    producto = get_object_or_404(
        Producto.objects.select_related('empresa'),
        producto_id=producto_id
    )
    
    # Obtener ventas del producto
    ventas_producto = Venta.objects.filter(producto=producto).select_related('cliente', 'usuario')
    
    # Estadísticas del producto
    total_ventas = ventas_producto.count()
    monto_total = ventas_producto.aggregate(total=Sum('monto_venta'))['total'] or 0
    
    context = {
        'producto': producto,
        'ventas_producto': ventas_producto,
        'total_ventas': total_ventas,
        'monto_total': monto_total,
    }
    return render(request, 'productos/detalle_producto.html', context)

@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            
            # Si es una request AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Producto creado exitosamente!'
                })
            # Si no es AJAX, redireccionar normalmente
            return redirect('lista_productos')
        else:
            # Si es AJAX y hay errores
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = ProductoForm()
    
    return render(request, 'tables/productos-list.html', {'form': form})

@login_required
def editar_producto(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        producto = get_object_or_404(Producto, producto_id=producto_id)
        form = ProductoForm(request.POST, instance=producto)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('lista_productos')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    
    return redirect('lista_productos')

@login_required
def eliminar_producto(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        
        if producto_id:
            try:
                producto = get_object_or_404(Producto, producto_id=producto_id)
                nombre_producto = producto.nombre_producto
                producto.delete()
                messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al eliminar el producto: {str(e)}')
        else:
            messages.error(request, 'No se proporcionó un ID de producto válido.')
    
    return redirect('lista_productos')


# Lista de Empresas
@login_required
def lista_empresas(request):
    # Filtros
    comision_min = request.GET.get('comision_min', '')
    comision_max = request.GET.get('comision_max', '')
    email = request.GET.get('email', '')
    
    empresas = EmpresaSocia.objects.all()
    
    # Aplicar filtros
    if comision_min:
        try:
            empresas = empresas.filter(comision_aplicable__gte=float(comision_min))
        except ValueError:
            pass
    
    if comision_max:
        try:
            empresas = empresas.filter(comision_aplicable__lte=float(comision_max))
        except ValueError:
            pass
    
    if email:
        empresas = empresas.filter(contacto_email__icontains=email)
    
    # Estadísticas
    total_empresas = empresas.count()
    
    if empresas.exists():
        comision_promedio = empresas.aggregate(avg=Avg('comision_aplicable'))['avg']
        comision_promedio = round(comision_promedio, 2)
    else:
        comision_promedio = 0
    
    # Empresas registradas hoy
    hoy = timezone.now().date()
    empresas_hoy = empresas.filter(fecha_creacion__date=hoy).count()
    
    # Contar productos por empresa
    empresas = empresas.annotate(
        productos_count=Count('producto')
    )
    
    # Contar empresas con email válido como contactos activos
    contactos_activos = empresas.filter(contacto_email__isnull=False).exclude(contacto_email='').count()
    
    # Paginación
    paginator = Paginator(empresas.order_by('-fecha_creacion'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas adicionales (opcionales)
    empresa_mayor_comision = empresas.order_by('-comision_aplicable').first()
    empresa_menor_comision = empresas.order_by('comision_aplicable').first()
    empresa_mas_productos = empresas.order_by('-productos_count').first()
    
    context = {
        'empresas': page_obj,
        'total_empresas': total_empresas,
        'comision_promedio': comision_promedio,
        'contactos_activos': contactos_activos,
        'empresas_hoy': empresas_hoy,
        # Estadísticas adicionales
        'empresa_mayor_comision': empresa_mayor_comision,
        'empresa_menor_comision': empresa_menor_comision, 
        'empresa_mas_productos': empresa_mas_productos,
    }

    
    return render(request, 'tables/empresas-list.html', context)
    
@login_required
def crear_empresa(request):
    if request.method == 'POST':
        form = EmpresaSociaForm(request.POST)
        if form.is_valid():
            empresa = form.save()
            messages.success(request, f'Empresa "{empresa.nombre_empresa}" creada exitosamente.')
            return redirect('lista_empresas')
        else:
            # Si hay errores, mostrar el formulario con los errores
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = EmpresaSociaForm()
    
    # Si es GET o hay errores, mostrar la lista con el formulario
    return redirect('lista_empresas')

@login_required
def editar_empresa(request, empresa_id):
    empresa = get_object_or_404(EmpresaSocia, empresa_id=empresa_id)
    
    if request.method == 'POST':
        form = EmpresaSociaForm(request.POST, instance=empresa)
        if form.is_valid():
            empresa = form.save()
            messages.success(request, f'Empresa "{empresa.nombre_empresa}" actualizada exitosamente.')
            return redirect('lista_empresas')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = EmpresaSociaForm(instance=empresa)
    
    context = {
        'form': form,
        'empresa': empresa,
    }
    return render(request, 'empresas/editar_empresa.html', context)

@login_required
def obtener_datos_empresa(request, empresa_id):
    empresa = get_object_or_404(EmpresaSocia, empresa_id=empresa_id)
    
    datos_empresa = {
        'nombre_empresa': empresa.nombre_empresa,
        'comision_aplicable': str(empresa.comision_aplicable),
        'contacto_email': empresa.contacto_email,
        'telefono': empresa.telefono,
        'informacion_adicional': empresa.informacion_adicional,
    }
    
    return JsonResponse(datos_empresa)

@login_required
def eliminar_empresa(request):
    if request.method == 'POST':
        empresa_id = request.POST.get('empresa_id')
        
        if empresa_id:
            try:
                with transaction.atomic():
                    empresa = get_object_or_404(EmpresaSocia, empresa_id=empresa_id)
                    nombre_empresa = empresa.nombre_empresa
                    
                    # Contar productos antes de eliminar para el mensaje
                    total_productos = empresa.producto_set.count()
                    
                    # Eliminar la empresa (esto eliminará en cascada los productos debido al CASCADE)
                    empresa.delete()
                    
                    # Mensaje informativo
                    if total_productos > 0:
                        messages.success(
                            request, 
                            f'Empresa "{nombre_empresa}" y sus {total_productos} producto(s) asociado(s) fueron eliminados exitosamente.'
                        )
                    else:
                        messages.success(
                            request, 
                            f'Empresa "{nombre_empresa}" eliminada exitosamente.'
                        )
                        
            except EmpresaSocia.DoesNotExist:
                messages.error(request, 'La empresa que intentas eliminar no existe.')
            except Exception as e:
                messages.error(request, f'Error al eliminar la empresa: {str(e)}')
        else:
            messages.error(request, 'No se proporcionó un ID de empresa válido.')
    
    return redirect('lista_empresas')

@login_required
def lista_ventas(request):
    # Filtros
    estado = request.GET.get('estado', '')
    monto_min = request.GET.get('monto_min', '')
    monto_max = request.GET.get('monto_max', '')
    fecha = request.GET.get('fecha', '')
    
    ventas = Venta.objects.select_related('producto', 'cliente', 'usuario').all()
    
    # Aplicar filtros
    if estado:
        ventas = ventas.filter(estado=estado)
    
    if monto_min:
        try:
            ventas = ventas.filter(monto_venta__gte=float(monto_min))
        except ValueError:
            pass
    
    if monto_max:
        try:
            ventas = ventas.filter(monto_venta__lte=float(monto_max))
        except ValueError:
            pass
    
    if fecha:
        ventas = ventas.filter(fecha_inicio=fecha)
    
    # Estadísticas
    total_ventas = ventas.count()
    
    if ventas.exists():
        ingresos_totales = ventas.aggregate(total=Sum('monto_venta'))['total'] or 0
        ingresos_totales = round(ingresos_totales, 2)
    else:
        ingresos_totales = 0
    
    total_clientes = Cliente.objects.count()
    
    # Ventas realizadas hoy
    hoy = timezone.now().date()
    ventas_hoy = ventas.filter(fecha_creacion__date=hoy).count()
    
    # Paginación
    paginator = Paginator(ventas.order_by('-fecha_creacion'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    productos = Producto.objects.select_related('empresa').all()
    clientes = Cliente.objects.all()
    usuarios = Usuario.objects.all()
    
    context = {
        'ventas': page_obj,
        'total_ventas': total_ventas,
        'ingresos_totales': ingresos_totales,
        'total_clientes': total_clientes,
        'ventas_hoy': ventas_hoy,
        'productos': productos,
        'clientes': clientes,
        'usuarios': usuarios,
        'ESTADO_CHOICES': Venta.ESTADO_CHOICES,
        'form': VentaForm(),  # Si estás usando formularios Django
    }

    return render(request, 'tables/ventas-list.html', context)

@login_required
def crear_venta(request):
    if request.method == 'POST':
        print("=== DEBUG CREAR VENTA ===")
        print("Datos POST:", dict(request.POST))
        
        form = VentaForm(request.POST)
        
        if form.is_valid():
            try:
                venta = form.save()
                print(f"✅ Venta creada: ID {venta.venta_id}, Usuario: {venta.usuario_id}")
                messages.success(request, f'Venta #{venta.venta_id} creada exitosamente.')
                return redirect('lista_ventas')  # Solo redirect cuando es exitoso
            except Exception as e:
                print(f"❌ Error al guardar: {str(e)}")
                messages.error(request, f'Error al crear la venta: {str(e)}')
        else:
            print("❌ Errores del formulario:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    # Si hay errores, volver a la misma página
    return lista_ventas(request)  # Reutiliza la vista principal


@login_required
def editar_venta(request):
    if request.method == 'POST':
        venta_id = request.POST.get('venta_id')
        if venta_id:
            try:
                venta = get_object_or_404(Venta, venta_id=venta_id)
                
                # Verificar si la venta puede ser editada
                if venta.estado in ['Finalizado', 'Cancelado']:
                    messages.error(request, 'No se puede editar una venta finalizada o cancelada')
                    return redirect('lista_ventas')
                
                form = VentaForm(request.POST, instance=venta)
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Venta #{venta.venta_id} actualizada exitosamente.')
                    return redirect('lista_ventas')
                else:
                    messages.error(request, 'Por favor corrige los errores del formulario.')
            except Venta.DoesNotExist:
                messages.error(request, 'La venta que intentas editar no existe.')
        else:
            messages.error(request, 'No se proporcionó un ID de venta válido.')
    
    return redirect('lista_ventas')


# Vista para obtener datos de una venta (opcional, si quieres usar AJAX)
@login_required
def obtener_datos_venta(request, venta_id):
    try:
        venta = get_object_or_404(Venta, venta_id=venta_id)
        data = {
            'venta_id': venta.venta_id,
            'producto_id': venta.producto.producto_id,
            'cliente_id': venta.cliente.cliente_id,
            'usuario_id': venta.usuario.usuario_id,
            'fecha_inicio': venta.fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': venta.fecha_fin.strftime('%Y-%m-%d') if venta.fecha_fin else '',
            'estado': venta.estado,
            'monto_venta': str(venta.monto_venta),
            'fecha_creacion': venta.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'puede_editarse': venta.estado not in ['Finalizado', 'Cancelado']
        }
        return JsonResponse(data)
    except Venta.DoesNotExist:
        return JsonResponse({'error': 'Venta no encontrada'}, status=404)

@login_required
def eliminar_venta(request):
    if request.method == 'POST':
        venta_id = request.POST.get('venta_id')
        
        if venta_id:
            try:
                with transaction.atomic():
                    venta = get_object_or_404(Venta, venta_id=venta_id)
                    
                    # Verificar si la venta puede ser eliminada
                    if venta.estado in ['Finalizado', 'Cancelado']:
                        messages.error(request, 'No se puede eliminar una venta finalizada o cancelada.')
                        return redirect('lista_ventas')
                    
                    # Guardar información para el mensaje
                    venta_info = f"Venta #{venta.venta_id} - {venta.cliente.nombre_cliente} - {venta.producto.nombre_producto}"
                    
                    # Eliminar la venta
                    venta.delete()
                    
                    messages.success(request, f'Venta "{venta_info}" eliminada exitosamente.')
                    
            except Venta.DoesNotExist:
                messages.error(request, 'La venta que intentas eliminar no existe.')
            except Exception as e:
                messages.error(request, f'Error al eliminar la venta: {str(e)}')
        else:
            messages.error(request, 'No se proporcionó un ID de venta válido.')
    
    return redirect('lista_ventas')

@login_required
def lista_clientes(request):
    # Filtros
    email = request.GET.get('email', '')
    telefono = request.GET.get('telefono', '')
    nombre = request.GET.get('nombre', '')
    
    clientes = Cliente.objects.all()
    
    # Aplicar filtros
    if email:
        clientes = clientes.filter(email__icontains=email)
    
    if telefono:
        clientes = clientes.filter(telefono__icontains=telefono)
    
    if nombre:
        clientes = clientes.filter(nombre_cliente__icontains=nombre)
    
    # Estadísticas
    total_clientes = clientes.count()
    clientes_con_email = clientes.filter(email__isnull=False).exclude(email='').count()
    clientes_con_telefono = clientes.filter(telefono__isnull=False).exclude(telefono='').count()
    
    # Clientes registrados hoy
    hoy = timezone.now().date()
    clientes_hoy = clientes.filter(fecha_creacion__date=hoy).count()
    
    # Anotar cada cliente con el número de ventas
    clientes = clientes.annotate(
        ventas_count=Count('venta')
    )
    
    # Paginación
    paginator = Paginator(clientes.order_by('-fecha_creacion'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'clientes': page_obj,
        'total_clientes': total_clientes,
        'clientes_con_email': clientes_con_email,
        'clientes_con_telefono': clientes_con_telefono,
        'clientes_hoy': clientes_hoy,
        'form': ClienteForm(),
    }

    return render(request, 'tables/clientes-list.html', context)

@login_required
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente "{cliente.nombre_cliente}" creado exitosamente.')
            return redirect('lista_clientes')
        else:
            # Si hay errores, mostrar el formulario con los errores
            messages.error(request, 'Por favor corrige los errores del formulario.')
            
            # Volver a cargar la lista con el formulario y errores
            clientes = Cliente.objects.all().annotate(ventas_count=Count('venta'))
            paginator = Paginator(clientes.order_by('-fecha_creacion'), 12)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context = {
                'clientes': page_obj,
                'total_clientes': clientes.count(),
                'clientes_con_email': clientes.filter(email__isnull=False).exclude(email='').count(),
                'clientes_con_telefono': clientes.filter(telefono__isnull=False).exclude(telefono='').count(),
                'clientes_hoy': clientes.filter(fecha_creacion__date=timezone.now().date()).count(),
                'form': form,
            }
            return render(request, 'clientes/lista_clientes.html', context)
    
    return redirect('lista_clientes')

@login_required
def editar_cliente(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        
        if cliente_id:
            try:
                cliente = get_object_or_404(Cliente, cliente_id=cliente_id)
                form = ClienteForm(request.POST, instance=cliente)
                
                if form.is_valid():
                    cliente = form.save()
                    messages.success(request, f'Cliente "{cliente.nombre_cliente}" actualizado exitosamente.')
                    return redirect('lista_clientes')
                else:
                    messages.error(request, 'Por favor corrige los errores del formulario.')
                    
                    # Volver a cargar la lista con el formulario y errores
                    clientes = Cliente.objects.all().annotate(ventas_count=Count('venta'))
                    paginator = Paginator(clientes.order_by('-fecha_creacion'), 12)
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    
                    context = {
                        'clientes': page_obj,
                        'total_clientes': clientes.count(),
                        'clientes_con_email': clientes.filter(email__isnull=False).exclude(email='').count(),
                        'clientes_con_telefono': clientes.filter(telefono__isnull=False).exclude(telefono='').count(),
                        'clientes_hoy': clientes.filter(fecha_creacion__date=timezone.now().date()).count(),
                        'form': form,
                    }
                    return render(request, 'clientes/lista_clientes.html', context)
                    
            except Cliente.DoesNotExist:
                messages.error(request, 'El cliente que intentas editar no existe.')
        else:
            messages.error(request, 'No se proporcionó un ID de cliente válido.')
    
    return redirect('lista_clientes')

@login_required
def eliminar_cliente(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        
        if cliente_id:
            try:
                cliente = get_object_or_404(Cliente, cliente_id=cliente_id)
                
                # Verificar si el cliente tiene ventas asociadas
                ventas_count = Venta.objects.filter(cliente=cliente).count()
                nombre_cliente = cliente.nombre_cliente or "Cliente sin nombre"
                
                if ventas_count > 0:
                    # Si tiene ventas, eliminarlas en cascada o mostrar advertencia
                    # Opción 1: Eliminar en cascada (descomenta si quieres esta opción)
                    # Venta.objects.filter(cliente=cliente).delete()
                    # cliente.delete()
                    # messages.success(request, f'Cliente "{nombre_cliente}" y sus {ventas_count} venta(s) asociada(s) fueron eliminados exitosamente.')
                    
                    # Opción 2: Mostrar error (recomendado para mantener integridad de datos)
                    messages.error(request, f'No se puede eliminar el cliente "{nombre_cliente}" porque tiene {ventas_count} venta(s) asociada(s).')
                    return redirect('lista_clientes')
                else:
                    # Si no tiene ventas, eliminar normalmente
                    cliente.delete()
                    messages.success(request, f'Cliente "{nombre_cliente}" eliminado exitosamente.')
                    
            except Cliente.DoesNotExist:
                messages.error(request, 'El cliente que intentas eliminar no existe.')
            except Exception as e:
                messages.error(request, f'Error al eliminar el cliente: {str(e)}')
        else:
            messages.error(request, 'No se proporcionó un ID de cliente válido.')
    
    return redirect('lista_clientes')

# Vista opcional para obtener datos del cliente via AJAX
@login_required
def obtener_datos_cliente(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, cliente_id=cliente_id)
        
        # Obtener estadísticas de ventas
        ventas = Venta.objects.filter(cliente=cliente)
        total_ventas = ventas.count()
        monto_total = ventas.aggregate(total=Sum('monto_venta'))['total'] or 0
        ventas_activas = ventas.exclude(estado__in=['Finalizado', 'Cancelado']).count()
        promedio_venta = monto_total / total_ventas if total_ventas > 0 else 0
        
        data = {
            'cliente_id': cliente.cliente_id,
            'nombre_cliente': cliente.nombre_cliente,
            'email': cliente.email,
            'telefono': cliente.telefono,
            'direccion': cliente.direccion,
            'fecha_creacion': cliente.fecha_creacion.strftime('%d/%m/%Y'),
            'total_ventas': total_ventas,
            'monto_total': float(monto_total),
            'ventas_activas': ventas_activas,
            'promedio_venta': float(promedio_venta),
            'ventas_count': total_ventas,  # Para el modal de eliminación
        }
        return JsonResponse(data)
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)




@login_required
def lista_reglas_comisiones(request):
    return render(request, 'tables/reglas-comisiones-list.html')

@login_required
def lista_equipos(request):
    # Obtener parámetros de filtro
    nombre = request.GET.get('nombre', '')
    fecha_creacion = request.GET.get('fecha_creacion', '')
    
    # Construir queryset base
    equipos_list = Equipo.objects.all().order_by('-fecha_creacion')
    
    # Aplicar filtros
    if nombre:
        equipos_list = equipos_list.filter(nombre_equipo__icontains=nombre)
    
    if fecha_creacion:
        equipos_list = equipos_list.filter(fecha_creacion__date=fecha_creacion)
    
    # Paginación
    paginator = Paginator(equipos_list, 10)
    page_number = request.GET.get('page')
    equipos = paginator.get_page(page_number)
    
    # Estadísticas
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    
    total_equipos = Equipo.objects.count()
    equipos_hoy = Equipo.objects.filter(fecha_creacion__date=hoy).count()
    equipos_mes = Equipo.objects.filter(fecha_creacion__date__gte=inicio_mes).count()
    
    context = {
        'equipos': equipos,
        'total_equipos': total_equipos,
        'equipos_hoy': equipos_hoy,
        'equipos_mes': equipos_mes,
        'filtros': {
            'nombre': nombre,
            'fecha_creacion': fecha_creacion,
        }
    }

    return render(request, 'tables/equipos-list.html', context)

def agregar_equipo(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo creado exitosamente.')
            return redirect('lista_equipos')
        else:
            messages.error(request, 'Error al crear el equipo. Por favor, revise los datos.')
    else:
        form = EquipoForm()
    
    return render(request, 'partials/equipos-modales/modal-agregar-equipo.html', {'form': form})

def editar_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, equipo_id=equipo_id)
    
    if request.method == 'POST':
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo actualizado exitosamente.')
            return redirect('lista_equipos')
        else:
            messages.error(request, 'Error al actualizar el equipo. Por favor, revise los datos.')
    else:
        form = EquipoForm(instance=equipo)
    
    # Si es una petición GET, redirige a la lista (o maneja como prefieras)
    return redirect('lista_equipos')

def eliminar_equipo(request, equipo_id):

    equipo = get_object_or_404(Equipo, equipo_id=equipo_id)
    
    if request.method == 'POST':
        nombre_equipo = equipo.nombre_equipo
        equipo.delete()
        messages.success(request, f'Equipo "{nombre_equipo}" eliminado exitosamente.')
        return redirect('lista_equipos')

    return render(request, 'partials/equipos-modales/modal-eliminar-equipo.html', {'equipo': equipo})

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, f'Usuario {user.username} creado exitosamente.')
            return redirect('crear_usuario')
    else:
        form = UsuarioForm()

    return render(request, 'partials/usuarios-modales/crear_usuario.html', {'form': form})
@login_required
def crear_rol(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Rol "{form.cleaned_data["role_name"]}" creado exitosamente.')
            return redirect('crear_rol')
    else:
        form = RoleForm()

    return render(request, 'partials/usuarios-modales/crear_rol.html', {'form': form})
@login_required
def asignar_rol(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        role_name = request.POST.get('role')

        user = Usuario.objects.get(pk=user_id)
        role = Role.objects.get(role_name=role_name)

        UserRole.objects.get_or_create(user_id=user, role=role)
        messages.success(request, f'Rol "{role.role_name}" asignado a {user.username}.')
        return redirect('asignar_rol')

    usuarios = Usuario.objects.all()
    roles = Role.objects.all()
    return render(request, 'partials/usuarios-modales/asignar_rol.html', {'usuarios': usuarios, 'roles': roles})



def lista_comisiones(request):
    # Obtener parámetros de filtrado
    estado_filter = request.GET.get('estado', '')
    monto_min = request.GET.get('monto_min', '')
    monto_max = request.GET.get('monto_max', '')
    
    # Consulta base
    comisiones = Comision.objects.select_related('usuario', 'venta', 'regla').all()
    
    # Aplicar filtros
    if estado_filter:
        comisiones = comisiones.filter(estado=estado_filter)
    
    if monto_min:
        comisiones = comisiones.filter(monto_comision__gte=monto_min)
    
    if monto_max:
        comisiones = comisiones.filter(monto_comision__lte=monto_max)
    
    # Estadísticas generales
    total_comisiones = comisiones.count()
    monto_total_comisiones = comisiones.aggregate(Sum('monto_comision'))['monto_comision__sum'] or 0
    comisiones_pagadas = comisiones.filter(estado='Pagada').count()
    comisiones_pendientes = comisiones.filter(estado='Pendiente').count()
    
    # Estadísticas destacadas
    comision_mayor_monto = comisiones.order_by('-monto_comision').first()
    comision_menor_monto = comisiones.order_by('monto_comision').first()
    promedio_comisiones = comisiones.aggregate(Avg('monto_comision'))['monto_comision__avg'] or 0
    
    # Paginación
    paginator = Paginator(comisiones, 10)  # 10 comisiones por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener datos para los formularios en modales
    usuarios = Usuario.objects.all()
    ventas = Venta.objects.all()
    reglas = ReglaComision.objects.all()
    
    context = {
        'comisiones': page_obj,
        'total_comisiones': total_comisiones,
        'monto_total_comisiones': monto_total_comisiones,
        'comisiones_pagadas': comisiones_pagadas,
        'comisiones_pendientes': comisiones_pendientes,
        'comision_mayor_monto': comision_mayor_monto,
        'comision_menor_monto': comision_menor_monto,
        'promedio_comisiones': promedio_comisiones,
        'usuarios': usuarios,
        'ventas': ventas,
        'reglas': reglas,
    }
    
    return render(request, 'tables/comisiones-list.html', context)

def agregar_comision(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            usuario_id = request.POST.get('usuario')
            venta_id = request.POST.get('venta')
            regla_id = request.POST.get('regla')
            monto_comision = request.POST.get('monto_comision')
            estado = request.POST.get('estado')
            fecha_pagada = request.POST.get('fecha_pagada')
            
            # Validaciones básicas
            if not all([usuario_id, venta_id, regla_id, monto_comision, estado]):
                messages.error(request, 'Todos los campos obligatorios deben ser completados.')
                return redirect('lista_comisiones')
            
            # Crear la comisión
            comision = Comision(
                usuario_id=usuario_id,
                venta_id=venta_id,
                regla_id=regla_id,
                monto_comision=monto_comision,
                estado=estado,
                fecha_pagada=fecha_pagada if fecha_pagada else None
            )
            comision.save()
            
            messages.success(request, 'Comisión agregada correctamente.')
            
        except Exception as e:
            messages.error(request, f'Error al agregar la comisión: {str(e)}')
    
    return redirect('lista_comisiones')

def editar_comision(request, comision_id):
    comision = get_object_or_404(Comision, comision_id=comision_id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            usuario_id = request.POST.get('usuario')
            venta_id = request.POST.get('venta')
            regla_id = request.POST.get('regla')
            monto_comision = request.POST.get('monto_comision')
            estado = request.POST.get('estado')
            fecha_pagada = request.POST.get('fecha_pagada')
            
            # Validaciones básicas
            if not all([usuario_id, venta_id, regla_id, monto_comision, estado]):
                messages.error(request, 'Todos los campos obligatorios deben ser completados.')
                return redirect('lista_comisiones')
            
            # Actualizar la comisión
            comision.usuario_id = usuario_id
            comision.venta_id = venta_id
            comision.regla_id = regla_id
            comision.monto_comision = monto_comision
            comision.estado = estado
            comision.fecha_pagada = fecha_pagada if fecha_pagada else None
            
            # Si el estado cambia a Pagada y no hay fecha de pago, usar fecha actual
            if estado == 'Pagada' and not comision.fecha_pagada:
                comision.fecha_pagada = date.today()
            
            comision.save()
            
            messages.success(request, 'Comisión actualizada correctamente.')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar la comisión: {str(e)}')
    
    return redirect('lista_comisiones')

def eliminar_comision(request, comision_id):
    comision = get_object_or_404(Comision, comision_id=comision_id)
    
    if request.method == 'POST':
        try:
            comision_nombre = f"Comisión #{comision.comision_id} - {comision.usuario.nombre}"
            comision.delete()
            messages.success(request, f'Comisión {comision_nombre} eliminada correctamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar la comisión: {str(e)}')
    
    return redirect('lista_comisiones')

# Vista adicional para marcar comisión como pagada
def marcar_como_pagada(request, comision_id):
    comision = get_object_or_404(Comision, comision_id=comision_id)
    
    if request.method == 'POST':
        try:
            comision.estado = 'Pagada'
            comision.fecha_pagada = date.today()
            comision.save()
            
            messages.success(request, f'Comisión #{comision.comision_id} marcada como pagada.')
        except Exception as e:
            messages.error(request, f'Error al marcar la comisión como pagada: {str(e)}')
    
    return redirect('lista_comisiones')

# Vista para dashboard de comisiones (opcional)
def dashboard_comisiones(request):
    # Estadísticas generales
    comisiones_totales = Comision.objects.count()
    monto_total = Comision.objects.aggregate(Sum('monto_comision'))['monto_comision__sum'] or 0
    
    # Estadísticas por estado
    comisiones_por_estado = Comision.objects.values('estado').annotate(
        total=Count('comision_id'),
        monto_total=Sum('monto_comision')
    )
    
    # Top 5 usuarios con más comisiones
    top_usuarios = Comision.objects.values(
        'usuario__nombre', 
        'usuario__usuario_id'
    ).annotate(
        total_comisiones=Count('comision_id'),
        monto_total=Sum('monto_comision')
    ).order_by('-monto_total')[:5]
    
    # Comisiones por mes (últimos 6 meses)
    from django.db.models.functions import TruncMonth
    from datetime import datetime, timedelta
    
    seis_meses_atras = datetime.now() - timedelta(days=180)
    comisiones_por_mes = Comision.objects.filter(
        fecha_calculada__gte=seis_meses_atras
    ).annotate(
        mes=TruncMonth('fecha_calculada')
    ).values('mes').annotate(
        total=Count('comision_id'),
        monto_total=Sum('monto_comision')
    ).order_by('mes')
    
    context = {
        'comisiones_totales': comisiones_totales,
        'monto_total': monto_total,
        'comisiones_por_estado': comisiones_por_estado,
        'top_usuarios': top_usuarios,
        'comisiones_por_mes': comisiones_por_mes,
    }
    
    return render(request, 'comisiones/dashboard_comisiones.html', context)



def lista_equipos(request):
    # Obtener parámetros de filtrado
    nombre_filter = request.GET.get('nombre', '')
    fecha_filter = request.GET.get('fecha', '')
    
    # Consulta base
    equipos = Equipo.objects.all().order_by('-fecha_creacion')
    
    # Aplicar filtros
    if nombre_filter:
        equipos = equipos.filter(nombre_equipo__icontains=nombre_filter)
    
    if fecha_filter:
        try:
            fecha_obj = datetime.strptime(fecha_filter, '%Y-%m-%d').date()
            equipos = equipos.filter(fecha_creacion__date=fecha_obj)
        except ValueError:
            # Si la fecha no es válida, ignorar el filtro
            pass
    
    # Estadísticas
    total_equipos = equipos.count()
    
    # Equipos creados hoy
    hoy = timezone.now().date()
    equipos_hoy = Equipo.objects.filter(fecha_creacion__date=hoy).count()
    
    # Equipos con descripción
    equipos_con_descripcion = Equipo.objects.exclude(descripcion__isnull=True).exclude(descripcion='').count()
    
    # Paginación
    paginator = Paginator(equipos, 8)  # 8 equipos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'equipos': page_obj,
        'total_equipos': total_equipos,
        'equipos_hoy': equipos_hoy,
        'equipos_con_descripcion': equipos_con_descripcion,
    }
    
    return render(request, 'tables/equipos-list.html', context)

def agregar_equipo(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre_equipo = request.POST.get('nombre_equipo', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            
            # Validaciones
            if not nombre_equipo:
                messages.error(request, 'El nombre del equipo es obligatorio.')
                return redirect('lista_equipos')
            
            if len(nombre_equipo) > 100:
                messages.error(request, 'El nombre del equipo no puede tener más de 100 caracteres.')
                return redirect('lista_equipos')
            
            # Verificar si ya existe un equipo con el mismo nombre
            if Equipo.objects.filter(nombre_equipo__iexact=nombre_equipo).exists():
                messages.error(request, 'Ya existe un equipo con ese nombre.')
                return redirect('lista_equipos')
            
            # Crear el equipo
            equipo = Equipo(
                nombre_equipo=nombre_equipo,
                descripcion=descripcion if descripcion else None
            )
            equipo.save()
            
            messages.success(request, f'Equipo "{nombre_equipo}" creado correctamente.')
            
        except Exception as e:
            messages.error(request, f'Error al crear el equipo: {str(e)}')
    
    return redirect('lista_equipos')

def editar_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, equipo_id=equipo_id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre_equipo = request.POST.get('nombre_equipo', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            
            # Validaciones
            if not nombre_equipo:
                messages.error(request, 'El nombre del equipo es obligatorio.')
                return redirect('lista_equipos')
            
            if len(nombre_equipo) > 100:
                messages.error(request, 'El nombre del equipo no puede tener más de 100 caracteres.')
                return redirect('lista_equipos')
            
            # Verificar si ya existe otro equipo con el mismo nombre (excluyendo el actual)
            if Equipo.objects.filter(nombre_equipo__iexact=nombre_equipo).exclude(equipo_id=equipo_id).exists():
                messages.error(request, 'Ya existe otro equipo con ese nombre.')
                return redirect('lista_equipos')
            
            # Actualizar el equipo
            equipo.nombre_equipo = nombre_equipo
            equipo.descripcion = descripcion if descripcion else None
            equipo.save()
            
            messages.success(request, f'Equipo "{nombre_equipo}" actualizado correctamente.')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el equipo: {str(e)}')
    
    return redirect('lista_equipos')

def eliminar_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, equipo_id=equipo_id)
    
    if request.method == 'POST':
        try:
            nombre_equipo = equipo.nombre_equipo
            equipo.delete()
            messages.success(request, f'Equipo "{nombre_equipo}" eliminado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el equipo: {str(e)}')
    
    return redirect('lista_equipos')

# Vista para obtener detalles del equipo (opcional, para APIs)
def detalle_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, equipo_id=equipo_id)
    
    data = {
        'equipo_id': equipo.equipo_id,
        'nombre_equipo': equipo.nombre_equipo,
        'descripcion': equipo.descripcion,
        'fecha_creacion': equipo.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
    }
    
    return JsonResponse(data)

# Vista para dashboard de equipos (opcional)
def dashboard_equipos(request):
    # Estadísticas generales
    total_equipos = Equipo.objects.count()
    
    # Equipos por mes (últimos 6 meses)
    
    seis_meses_atras = timezone.now() - timezone.timedelta(days=180)
    
    equipos_por_mes = Equipo.objects.filter(
        fecha_creacion__gte=seis_meses_atras
    ).annotate(
        mes=TruncMonth('fecha_creacion')
    ).values('mes').annotate(
        total=Count('equipo_id')
    ).order_by('mes')
    
    # Equipos con y sin descripción
    equipos_con_desc = Equipo.objects.exclude(descripcion__isnull=True).exclude(descripcion='').count()
    equipos_sin_desc = total_equipos - equipos_con_desc
    
    context = {
        'total_equipos': total_equipos,
        'equipos_por_mes': list(equipos_por_mes),
        'equipos_con_desc': equipos_con_desc,
        'equipos_sin_desc': equipos_sin_desc,
    }
    
    return render(request, 'equipos/dashboard_equipos.html', context)

