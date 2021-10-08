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
    servicios = Servicio.objects.all()
    context = {'servicios': servicios}
    return render(request, 'verServicios.html', context)

@login_required(login_url='/ingresar')
def verPerfil(request):
    servicios = Servicio.objects.filter(idUsuario=request.user.id)
    context = {'servicios': servicios}
    return render(request, 'profile.html', context)

@login_required(login_url='/ingresar')
def servicio(request, id):
    if request.method=='POST':
        if Servicio.objects.get(id=request.POST.get('id')).idUsuario == request.user:
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

@login_required(login_url='/ingresar')
def deleServicioUsuario(request):
    if Servicio.objects.get(id=request.POST.get('id')).idUsuario == request.user:
        Servicio.objects.filter(id=request.POST.get('id')).delete()
        return HttpResponseRedirect('/exito')
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
            print(request.user)
            print("Ha recibido un nuevo mensaje de " + request.user.username)
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
        return render(request, 'notificaciones.html')