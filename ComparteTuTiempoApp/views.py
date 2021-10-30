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

def inicio(request):
    return render(request,'inicio.html')

def registro(request):
    if request.method=='POST':
        formulario = FormNuevoUsuario(request.POST)
        if formulario.is_valid():
            formulario.save()
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

@login_required(login_url='/ingresar')
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
            q_edad = Q(idUsuario__edad__icontains=edad) if form.cleaned_data['edad'] else Q(idUsuario__edad__gte=-1)
            categorias = form.cleaned_data['categorias']
            q_categorias = Q(categorias__icontains=categorias) if form.cleaned_data['categorias'] else (Q(categorias__isnull=False) | Q(categorias__isnull=True))
            servicios = Servicio.objects.filter((q_descripcion | q_titulo) & q_ciudad & q_edad & q_categorias).order_by(form.cleaned_data['orden'])
            form = FormBusqueda(request.POST)
            context = {'servicios': servicios, 'formulario': form}
            return render(request, 'verServicios.html', context)
        else:
            return HttpResponseRedirect('/error')
    else:
        servicios = Servicio.objects.all().order_by('creacion')
        form = FormBusqueda()
        context = {'servicios': servicios, 'formulario': form}
        return render(request, 'verServicios.html', context)

@login_required(login_url='/ingresar')
def verPerfil(request):
    servicios = Servicio.objects.filter(idUsuario=request.user.id)
    intercambios = Intercambio.objects.filter(Q(idUsuarioDa=request.user.id) | Q(idUsuarioRecibe=request.user.id))
    context = {'servicios': servicios, 'intercambios': intercambios}
    return render(request, 'profile.html', context)

@login_required(login_url='/ingresar')
def servicio(request, id):
    if request.method=='POST':
        lon = Intercambio.objects.filter(Q(idServicio=id) & Q(inicio__gte=timezone.now())).count()
        if Servicio.objects.get(id=request.POST.get('id')).idUsuario == request.user:
            if lon>=1:
                s = Servicio.objects.get(id=id)
                context = {'s': s, 'mensaje': "Todavía tiene intercambios pendientes con este servicio"}
                return render(request, 'detallesServicio.html', context)
            else:
                Servicio.objects.filter(id=request.POST.get('id')).delete()
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
    context = {'conversaciones': conversaciones}
    return render(request, 'conversaciones.html', context)

@login_required(login_url='/ingresar')
def conversacion(request, username):
    usuario2 = Usuario.objects.get(username=username)
    if Conversacion.objects.filter((Q(idUsuario1=request.user) & Q(idUsuario2=usuario2)) | (Q(idUsuario1=usuario2) & Q(idUsuario2=request.user))).exists():
        conversacion = Conversacion.objects.get((Q(idUsuario1=request.user) & Q(idUsuario2=usuario2)) | (Q(idUsuario1=usuario2) & Q(idUsuario2=request.user)))
        if request.method=='POST':
             form = FormNuevoMensaje(request.POST)
             if form.is_valid():
                 form.save(usuario1=request.user, usuario2=usuario2, conversacion= conversacion)
                 notificacion = Notificacion(descripcion="Ha recibido un nuevo mensaje de " + request.user.username, idUsuario=usuario2, url="/conversaciones/"+request.user.username)
                 notificacion.save()
                 return HttpResponseRedirect('/conversaciones/' + usuario2.username)
        else:
            form = FormNuevoMensaje()
            mensajes = Mensaje.objects.filter(idConversacion=conversacion).order_by('fechaHora')
            Notificacion.objects.filter(Q(idUsuario=request.user) & Q(descripcion="Ha recibido un nuevo mensaje de " + usuario2.username)).delete()
            context = {'mensajes': mensajes, 'formulario': form}
            return render(request, 'conversacion.html', context)
    else:
        conversacion = Conversacion(idUsuario1=request.user, idUsuario2=usuario2)
        conversacion.save()
        return HttpResponseRedirect('/conversaciones/'+usuario2.username)

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
    if request.method=='POST' and Servicio.objects.get(id=id).idUsuario != request.user:
        formulario = FormNuevoIntercambio(request.POST)
        if formulario.is_valid() and formulario.validate(request.user.saldo):
            servi = Servicio.objects.get(id=id)
            inter = formulario.save(servicio=servi, usuarioRecibe=request.user)
            notificacion = Notificacion(descripcion="Ha recibido una propuesta de intercambio " + request.user.username, idUsuario=servi.idUsuario, url="/intercambios/"+str(inter.id))
            notificacion.save()
            return HttpResponseRedirect('/exito')
    else:
        formulario = FormNuevoIntercambio()
    context = {'formulario': formulario}
    return render(request, 'formIntercambio.html', context)

@login_required(login_url='/ingresar')
def intercambio(request, id):
    inter = Intercambio.objects.get(id=id)
    if request.method=='POST':
        if 'id1' in request.POST:
            if inter.idUsuarioDa == request.user and inter.confirmacion == 0:
                if inter.idUsuarioRecibe.saldo-int((inter.fin-inter.inicio).total_seconds()//60)<0:
                    i = Intercambio.objects.get(id=id)
                    context = {'i': i, 'mensaje': "El usuario que solicitó el intercambio no cuenta con el saldo suficiente"}
                    return render(request, 'detallesIntercambio.html', context)
                elif inter.inicio<timezone.now():
                    i = Intercambio.objects.get(id=id)
                    context = {'i': i, 'mensaje': "La fecha solicitada para el intercambio ha pasado"}
                    inter.confirmacion = 3
                    inter.save()
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
            if inter.idUsuarioDa == request.user and inter.confirmacion != 2 and inter.confirmacion != 3 and timezone.now()<inter.inicio:
                notificacion = Notificacion(descripcion="El usuario " + request.user.username + " ha cancelado su intercambio", idUsuario=inter.idUsuarioRecibe, url="/intercambios/"+str(id))
                notificacion.save()
                inter.confirmacion = 3
                inter.save()
                inter.idUsuarioRecibe.saldo = inter.idUsuarioRecibe.saldo+int((inter.fin-inter.inicio).total_seconds()//60)
                inter.idUsuarioRecibe.save()
                return HttpResponseRedirect('/intercambios/' + str(id))
            elif inter.idUsuarioRecibe == request.user and inter.confirmacion != 2 and inter.confirmacion != 3:
                notificacion = Notificacion(descripcion="El usuario " + request.user.username + " ha cancelado su intercambio", idUsuario=inter.idUsuarioDa, url="/intercambios/"+str(id))
                notificacion.save()
                inter.confirmacion = 3
                inter.save()
                inter.idUsuarioRecibe.saldo = inter.idUsuarioRecibe.saldo+int((inter.fin-inter.inicio).total_seconds()//60)
                inter.idUsuarioRecibe.save()
                return HttpResponseRedirect('/intercambios/' + str(id))
            else:
                return HttpResponseRedirect('/error')
        elif 'nota' in request.POST and inter.idUsuarioRecibe==request.user and inter.confirmacion == 1:
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
        i = Intercambio.objects.get(id=id)
        valorar = timezone.now()>i.inicio
        context = {'i': i, 'valorar': valorar}
        return render(request, 'detallesIntercambio.html', context)
    return HttpResponseRedirect('/error')