from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Avg
from operator import attrgetter
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

def inicio(request):
    return render(request,'inicio.html')

def registro(request):
    if request.method=='POST':
        formulario = FormNuevoUsuario(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            admin = Usuario.objects.filter(is_staff=True).first()
            print(admin)
            if admin:
                c = Conversacion(idUsuario1=usuario,idUsuario2=admin)
                c.save()
                m = Mensaje(idUsuarioOrigen=admin, idUsuarioDestino=usuario,
                            idConversacion=c,fechaHora=timezone.now(), contenido="¡Bienvenido a ComparteTuTiempo! A partir de ahora formas parte de esta gran comunidad. "+
                            "Soy " + admin.username + ", el administrador de la web. Si tienes cualquier reclamación, duda o sugerencia, no dudes en contactar conmigo a través de este chat.")
                m.save()
                n = Notificacion(descripcion="Ha recibido un nuevo mensaje de " + admin.username, idUsuario=usuario, url="/conversaciones/"+str(admin.id))
                n.save()
            return HttpResponseRedirect('/exito')
    else:
        formulario = FormNuevoUsuario()
    context = {'formulario': formulario}
    return render(request, 'register.html', context)

def ingreso(request):
    if not request.user.is_anonymous:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        formulario = AuthenticationForm(request.POST)
        if formulario.is_valid:
            usuario = request.POST['username']
            clave = request.POST['password']
            acceso = authenticate(username=usuario, password=clave)
            if acceso is not None:
                if acceso.is_active:
                    login(request, acceso)
                    return HttpResponseRedirect('/')
                else:
                    return render(request, 'noActive.html')
            else:
                cx = {'err': "El usuario y/o la contraseña son incorrectos", 'formulario': formulario}
                return render(request, 'login.html', cx)
    else:
        formulario = AuthenticationForm()
    context = {'formulario': formulario}
    return render(request, 'login.html', context)

@login_required(login_url='/ingresar')
def cerrar(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required(login_url='/ingresar')
def crearServicioUsuario(request):
    if request.method=='POST':
        formulario = FormNuevoServUsuario(request.POST)
        if formulario.is_valid():
            formulario.presave(usuario=request.user)
            return HttpResponseRedirect('/exito')
    else:
        formulario = FormNuevoServUsuario()
    context = {'formulario': formulario}
    return render(request, 'formServicio.html', context)

def verServicios(request):
    if request.method=='POST':
        form = FormBusqueda(request.POST)
        if form.is_valid():
            descripcion = form.cleaned_data['descripcion']
            q_descripcion = Q(descripcion__icontains=descripcion) if form.cleaned_data['descripcion'] else Q(descripcion__icontains='')
            q_titulo = Q(nombre__icontains=descripcion) if form.cleaned_data['descripcion'] else Q(nombre__icontains='')
            ciudad = form.cleaned_data['ciudad']
            q_ciudad = Q(idUsuario__ciudad__icontains=ciudad) if form.cleaned_data['ciudad'] else Q(idUsuario__ciudad__icontains='')
            edad = form.cleaned_data['edad']
            q_edad = Q(idUsuario__edad=edad) if form.cleaned_data['edad']!=None else Q(idUsuario__edad__gte=-1)
            categorias = form.cleaned_data['categorias']
            q_categorias = Q(categorias__in=categorias)
            if form.cleaned_data['categorias']:
                servicios = Servicio.objects.filter((q_descripcion | q_titulo) & q_ciudad & q_edad & q_categorias & Q(estado=True)).order_by(form.cleaned_data['orden'])
            else:
                servicios = Servicio.objects.filter((q_descripcion | q_titulo) & q_ciudad & q_edad & Q(estado=True)).order_by(form.cleaned_data['orden'])
            form = FormBusqueda(request.POST)
            context = {'servicios': servicios, 'formulario': form}
            print(servicios)
            return render(request, 'verServicios.html', context)
        else:
            return HttpResponseRedirect('/error')
    else:
        servicios = Servicio.objects.filter(estado=True).order_by('-creacion')
        form = FormBusqueda()
        context = {'servicios': servicios, 'formulario': form}
        return render(request, 'verServicios.html', context)

@login_required(login_url='/ingresar')
def verPerfil(request):
    servicios = Servicio.objects.filter(idUsuario=request.user.id)
    intercambios = Intercambio.objects.filter(Q(idUsuarioDa=request.user.id) | Q(idUsuarioRecibe=request.user.id))
    conversaciones = Conversacion.objects.filter(Q(idUsuario1=request.user.id) | Q(idUsuario2=request.user.id))
    context = {'servicios': servicios, 'intercambios': intercambios, 'conversaciones': conversaciones}
    return render(request, 'profile.html', context)

@login_required(login_url='/ingresar')
def servicio(request, id):
    if request.method=='POST':
        if Servicio.objects.get(id=request.POST.get('id')).idUsuario == request.user:
            lon = Intercambio.objects.filter(Q(idServicio=id) & Q(inicio__gte=timezone.now()) & Q(confirmacion=1)).count()
            if lon>=1 and Servicio.objects.get(id=id).estado:
                s = Servicio.objects.get(id=id)
                context = {'s': s, 'mensaje': "Todavía tiene intercambios pendientes con este servicio"}
                return render(request, 'detallesServicio.html', context)
            else:
                serv = Servicio.objects.get(id=request.POST.get('id'))
                serv.estado = not serv.estado
                serv.save()
                return HttpResponseRedirect('/exito')
        else:
            return HttpResponseRedirect('/error')
    else:
        s = Servicio.objects.get(id=id)
        context = {'s': s}
        return render(request, 'detallesServicio.html', context)

@login_required(login_url='/ingresar')
def editServicioUsuario(request, id):
    if Servicio.objects.get(id=id).idUsuario == request.user:
        my_record = Servicio.objects.get(id=id)
        if request.method=='POST':
            form = FormNuevoServUsuario(request.POST, instance=my_record)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/exito')
        else:
            form = FormNuevoServUsuario(instance=my_record)
        context = {'formulario': form}
        return render(request, 'formServicio.html', context)
    else:
        return HttpResponseRedirect('/error')

def exito(request):
    return render(request, 'exito.html')

def error(request):
    return render(request, 'error.html')

@login_required(login_url='/ingresar')
def conversaciones(request):
    conversaciones = Conversacion.objects.filter(Q(idUsuario1=request.user.id) | Q(idUsuario2=request.user.id))
    mensajes = []
    for c in conversaciones:
        if Mensaje.objects.filter(idConversacion=c):
            mensajes.append(Mensaje.objects.filter(idConversacion=c).latest('fechaHora').id)
    result = Mensaje.objects.filter(id__in=mensajes).order_by('-fechaHora')
    context = {'mensajes': result}
    return render(request, 'conversaciones.html', context)

@login_required(login_url='/ingresar')
def conversacion(request, id):
    usuario2 = Usuario.objects.get(id=id)
    if Conversacion.objects.filter((Q(idUsuario1=request.user) & Q(idUsuario2=usuario2)) | (Q(idUsuario1=usuario2) & Q(idUsuario2=request.user))).exists():
        conversacion = Conversacion.objects.get((Q(idUsuario1=request.user) & Q(idUsuario2=usuario2)) | (Q(idUsuario1=usuario2) & Q(idUsuario2=request.user)))
        if request.method=='POST':
             form = FormNuevoMensaje(request.POST)
             if form.is_valid():
                 form.save(usuario1=request.user, usuario2=usuario2, conversacion= conversacion)
                 notificacion = Notificacion(descripcion="Ha recibido un nuevo mensaje de " + request.user.username, idUsuario=usuario2, url="/conversaciones/"+str(request.user.id))
                 notificacion.save()
                 return HttpResponseRedirect('/conversaciones/' + str(usuario2.id))
             else:
                 form = FormNuevoMensaje()
                 mensajes = Mensaje.objects.filter(idConversacion=conversacion).order_by('-fechaHora')
                 Notificacion.objects.filter(Q(idUsuario=request.user) & Q(descripcion="Ha recibido un nuevo mensaje de " + usuario2.username)).delete()
                 context = {'mensajes': mensajes, 'formulario': form, 'usuario': usuario2}
                 return render(request, 'conversacion.html', context)
        else:
            form = FormNuevoMensaje()
            mensajes = Mensaje.objects.filter(idConversacion=conversacion).order_by('-fechaHora')
            Notificacion.objects.filter(Q(idUsuario=request.user) & Q(descripcion="Ha recibido un nuevo mensaje de " + usuario2.username)).delete()
            context = {'mensajes': mensajes, 'formulario': form, 'usuario': usuario2}
            return render(request, 'conversacion.html', context)
    else:
        if(request.user==usuario2):
            return HttpResponseRedirect('/inicio')
        else:
            conversacion = Conversacion(idUsuario1=request.user, idUsuario2=usuario2)
            conversacion.save()
        return HttpResponseRedirect('/conversaciones/'+str(usuario2.id))

@login_required(login_url='/ingresar')
def notificaciones(request):
    if request.method=='POST':
        if Notificacion.objects.get(id=request.POST.get('id')).idUsuario == request.user:
            Notificacion.objects.filter(id=request.POST.get('id')).delete()
            return HttpResponseRedirect('/notificaciones')
        else:
            return HttpResponseRedirect('/error')
    else:
        notificaciones = Notificacion.objects.filter(idUsuario=request.user).order_by('-id')
        context = {'notificaciones': notificaciones}
        return render(request, 'notificaciones.html', context)

@login_required(login_url='/ingresar')
def crearIntercambioUsuario(request, id):
    if Servicio.objects.get(id=id).estado:
        if request.method=='POST' and Servicio.objects.get(id=id).idUsuario != request.user:
            formulario = FormNuevoIntercambio(request.POST)
            if formulario.is_valid() and formulario.validate(request.user.saldo, request.user):
                servi = Servicio.objects.get(id=id)
                inter = formulario.save(servicio=servi, usuarioRecibe=request.user)
                notificacion = Notificacion(descripcion="Ha recibido una propuesta de intercambio " + request.user.username, idUsuario=servi.idUsuario, url="/intercambios/"+str(inter.id))
                notificacion.save()
                return HttpResponseRedirect('/exito')
        else:
            formulario = FormNuevoIntercambio()
        context = {'formulario': formulario}
        return render(request, 'formIntercambio.html', context)
    else:
        s = Servicio.objects.get(id=id)
        mensaje = 'Este servicio no se encuentra disponible'
        context = {'s': s, 'mensaje': mensaje}
        return render(request, 'detallesServicio.html', context)


@login_required(login_url='/ingresar')
def intercambio(request, id):
    inter = Intercambio.objects.get(id=id)
    if request.method=='POST':
        if 'id1' in request.POST:
            if inter.idUsuarioDa == request.user and inter.confirmacion == 0:
                if inter.idUsuarioRecibe.saldo-int((inter.fin-inter.inicio).total_seconds()//60)<0:
                    context = {'i': inter, 'mensaje': "El usuario que solicitó el intercambio no cuenta con el saldo suficiente"}
                    return render(request, 'detallesIntercambio.html', context)
                elif inter.inicio<timezone.now():
                    inter.confirmacion = 3
                    inter.save()
                    context = {'i': inter, 'mensaje': "La fecha solicitada para el intercambio ha pasado"}
                    return render(request, 'detallesIntercambio.html', context)
                elif Intercambio.objects.filter(Q(Q(inicio__range=[inter.inicio, inter.fin]) | Q(fin__range=[inter.inicio, inter.fin]) | Q(Q(inicio__lte=inter.inicio) & Q(fin__gte=inter.fin)) | Q(Q(inicio__gte=inter.inicio) & Q(fin__lte=inter.fin)) & Q(Q(idUsuarioDa=request.user) | Q(idUsuarioRecibe=request.user))) & Q(confirmacion=1)).count()>=1:
                    context = {'i': inter, 'mensaje': "Ya participas en un intercambio en ese rango de tiempo"}
                    return render(request, 'detallesIntercambio.html', context)
                elif Intercambio.objects.filter(Q(Q(inicio__range=[inter.inicio, inter.fin]) | Q(fin__range=[inter.inicio, inter.fin]) | Q(Q(inicio__lte=inter.inicio) & Q(fin__gte=inter.fin)) | Q(Q(inicio__gte=inter.inicio) & Q(fin__lte=inter.fin)) & Q(Q(idUsuarioDa=inter.idUsuarioRecibe) | Q(idUsuarioRecibe=inter.idUsuarioRecibe))) & Q(confirmacion=1)).count()>=1:
                    context = {'i': inter, 'mensaje': "El usuario que solicitó este intercambio ya ha acordado otro intercambio en este rango de tiempo"}
                    return render(request, 'detallesIntercambio.html', context)
                elif not inter.idServicio.estado:
                    context = {'i': inter, 'mensaje': "El servicio solicitado está desactivado"}
                    return render(request, 'detallesIntercambio.html', context)
                else:
                    inter.confirmacion = 1
                    inter.save()
                    notificacion = Notificacion(descripcion="El usuario " + request.user.username + " ha confirmado su intercambio", idUsuario=inter.idUsuarioRecibe, url="/intercambios/"+str(id))
                    notificacion.save()
                    inter.idUsuarioRecibe.saldo = inter.idUsuarioRecibe.saldo-int((inter.fin-inter.inicio).total_seconds()//60)
                    inter.idUsuarioRecibe.save()
                    return HttpResponseRedirect('/intercambios/' + str(id))
            else:
                return HttpResponseRedirect('/error')
        elif 'id2' in request.POST:
            if inter.idUsuarioDa == request.user and inter.confirmacion <= 2 and timezone.now()<inter.inicio:
                notificacion = Notificacion(descripcion="El usuario " + request.user.username + " ha cancelado su intercambio", idUsuario=inter.idUsuarioRecibe, url="/intercambios/"+str(id))
                notificacion.save()
                inter.confirmacion = 3
                inter.save()
                inter.idUsuarioRecibe.saldo = inter.idUsuarioRecibe.saldo+int((inter.fin-inter.inicio).total_seconds()//60)
                inter.idUsuarioRecibe.save()
                return HttpResponseRedirect('/intercambios/' + str(id))
            elif inter.idUsuarioRecibe == request.user and inter.confirmacion <= 2 and timezone.now()<inter.inicio:
                notificacion = Notificacion(descripcion="El usuario " + request.user.username + " ha cancelado su intercambio", idUsuario=inter.idUsuarioDa, url="/intercambios/"+str(id))
                notificacion.save()
                inter.confirmacion = 3
                inter.save()
                inter.idUsuarioRecibe.saldo = inter.idUsuarioRecibe.saldo+int((inter.fin-inter.inicio).total_seconds()//60)
                inter.idUsuarioRecibe.save()
                return HttpResponseRedirect('/intercambios/' + str(id))
            else:
                return HttpResponseRedirect('/error')
        elif 'nota' in request.POST and inter.idUsuarioRecibe==request.user and inter.confirmacion == 1 and timezone.now()>inter.inicio:
            inter.confirmacion=2
            inter.nota=request.POST['nota']
            inter.save()
            inter.idServicio.nota = round(inter.idServicio.intercambio_set.aggregate(Avg('nota')).get('nota__avg'), 2)
            inter.idServicio.save()
            inter.idUsuarioDa.valoracion = round(inter.idUsuarioDa.servicio_set.aggregate(Avg('nota')).get('nota__avg'), 2)
            inter.idUsuarioDa.saldo = inter.idUsuarioDa.saldo+int((inter.fin-inter.inicio).total_seconds()//60)
            inter.idUsuarioDa.save()
            notificacion = Notificacion(descripcion="El usuario " + request.user.username + " ha valorado su intercambio", idUsuario=inter.idUsuarioDa, url="/intercambios/"+str(id))
            notificacion.save()
            return HttpResponseRedirect('/intercambios/' + str(id))
        else:
            return HttpResponseRedirect('/error')
    elif inter.idUsuarioDa == request.user or inter.idUsuarioRecibe == request.user:
        valorar = timezone.now()>inter.inicio
        context = {'i': inter, 'valorar': valorar}
        return render(request, 'detallesIntercambio.html', context)
    return HttpResponseRedirect('/error')

@login_required(login_url='/ingresar')
def editUsuario(request):
    my_record = request.user
    if request.method=='POST':
        form = FormEditUsuario(request.POST, instance=my_record)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/exito')
    else:
        form = FormEditUsuario(instance=my_record)
    context = {'formulario': form}
    return render(request, 'editProfile.html', context)

@login_required(login_url='/ingresar')
def intercambios(request):
    if request.method=='POST':
        form = FormOrdenIntercambios(request.POST)
        if form.is_valid():
            descripcion = form.cleaned_data['descripcion']
            q_descripcion = Q(idServicio__descripcion__icontains=descripcion) | Q(idUsuarioRecibe__username__icontains=descripcion) | Q(idUsuarioDa__username__icontains=descripcion) | Q(idServicio__nombre__icontains=descripcion) if form.cleaned_data['descripcion'] else Q(idServicio__descripcion__icontains='')
            categorias = form.cleaned_data['categorias']
            q_categorias = Q(idServicio__categorias__in=categorias)
            if form.cleaned_data['categorias']:
                intercambios = Intercambio.objects.filter(Q(Q(idUsuarioDa=request.user) | Q(idUsuarioRecibe=request.user)) & q_descripcion & q_categorias).order_by(form.cleaned_data['orden'])
            else:
                intercambios = Intercambio.objects.filter(Q(Q(idUsuarioDa=request.user) | Q(idUsuarioRecibe=request.user)) & q_descripcion).order_by(form.cleaned_data['orden'])
            context = {'intercambios': intercambios, 'formulario': form}
            return render(request, 'verIntercambios.html', context)
    else:
        intercambios = Intercambio.objects.filter(Q(idUsuarioDa=request.user) | Q(idUsuarioRecibe=request.user))
        form = FormOrdenIntercambios()
        context = {'intercambios': intercambios, 'formulario': form}
        return render(request, 'verIntercambios.html', context)

@staff_member_required
def reiniciarCategorias(request):
    if request.user.is_staff:
        categorias = ['Coche y Moto','Belleza','Libros','Cámaras y fotografía','Teléfonos móviles y accesorios','Coleccionismo','Electrónica','Arte','Alimentación y bebidas','Salud y cuidado personal','Hogar','Diseño independiente','Industria, empresa y ciencia','Música','Oficina','Aire libre','Informática','Mascotas','Software','Deportes y aire libre','Bricolaje y herramientas','Videojuegos','Plantas y jardinería','Cocina']
        Categoria.objects.all().delete()
        for x in categorias:
            categoria = Categoria(nombre=x)
            categoria.save()
        return HttpResponseRedirect('/exito')

def error404(request,  *args, **kwargs):
    return HttpResponseRedirect('/')

def error403(request,  *args, **kwargs):
    return HttpResponseRedirect('/')

def error400(request,  *args, **kwargs):
    return HttpResponseRedirect('/error')