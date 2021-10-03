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