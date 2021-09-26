from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.http import HttpResponseRedirect

def inicio(request):
    return render(request,'inicio.html')

def registro(request):
    if request.method=='POST':
        formulario = FormNuevoUsuario(request.POST)
        if formulario.is_valid():
            formulario.save()
            return HttpResponseRedirect('/')
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
            return HttpResponseRedirect('/')
    else:
        formulario = FormNuevoServUsuario()
    context = {'formulario': formulario}
    return render(request, 'formServicio.html', context)

@login_required(login_url='/ingresar')
def verServicios(request):
    servicios = Servicio.objects.all()
    context = {'servicios': servicios}
    return render(request, 'verServicios.html', context)