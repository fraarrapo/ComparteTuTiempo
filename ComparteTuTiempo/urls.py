"""ComparteTuTiempo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ComparteTuTiempoApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registrar/', views.registro),
    path('ingresar/', views.ingreso),
    path('salir/', views.cerrar),
    path('', views.inicio),
    path('nuevoServicio/', views.crearServicioUsuario),
    path('servicios/', views.verServicios),
    path('perfil/', views.verPerfil),
    path('servicios/<int:id>/', views.servicio),
    path('servicios/editar/<int:id>/', views.editServicioUsuario),
    path('exito/', views.exito),
    path('error/', views.error),
    path('conversaciones/', views.conversaciones),
    path('conversaciones/<int:id>/', views.conversacion),
    path('notificaciones/', views.notificaciones),
    path('servicios/crearIntercambio/<int:id>/', views.crearIntercambioUsuario),
    path('intercambios/<int:id>/', views.intercambio),
    path('editarPerfil/', views.editUsuario),
    path('intercambios/', views.intercambios),
    path('reiniciarCategorias/', views.reiniciarCategorias),
]

handler404 = 'ComparteTuTiempoApp.views.error404'

handler403 = 'ComparteTuTiempoApp.views.error403'

handler400 = 'ComparteTuTiempoApp.views.error400'
