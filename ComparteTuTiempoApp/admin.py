from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

class UsuarioAdmin(UserAdmin):
    pass

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Intercambio)
admin.site.register(Servicio)
admin.site.register(Mensaje)
admin.site.register(Categoria)
admin.site.register(Conversacion)
# Register your models here.
