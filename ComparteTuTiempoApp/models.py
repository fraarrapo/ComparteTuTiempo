from django.db import models
from django.core.validators import *
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.forms import ModelForm
from django import forms

class Usuario(AbstractUser):
    ciudad = models.CharField(max_length=100)
    edad = models.PositiveIntegerField()
    contacto = models.CharField(max_length=50, blank=True)
    saldo = models.PositiveIntegerField(default=0)
    valoracion = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], null=True)

class Notificacion(models.Model):
    descripcion = models.CharField(max_length=300)
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    url = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return self.descripcion

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
            return self.nombre

class Servicio(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.CharField(validators=[MinLengthValidator(30)], max_length=500)
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    creacion = models.DateTimeField()
    nota = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], null=True)
    categorias = models.ManyToManyField(Categoria, blank=True)
    def __str__(self):
                return self.nombre

class Intercambio(models.Model):
    idServicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    idUsuarioRecibe = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='idUsuarioRecibe')
    idUsuarioDa = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='idUsuarioDa')
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    confirmacion = models.PositiveIntegerField(default=0)
    nota = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], null=True)
    def __str__(self):
                    return self.idUsuarioDa.__str__() + "--> " + self.idUsuarioRecibe.__str__()

class Conversacion(models.Model):
    idUsuario1 = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='idUsuario1')
    idUsuario2 = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='idUsuario2')
    def __str__(self):
                    return self.idUsuario1.__str__() + " <------> " + self.idUsuario2.__str__()

class Mensaje(models.Model):
    idUsuarioOrigen = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='idUsuarioOrigen')
    idUsuarioDestino = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='idUsuarioDestino')
    idConversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE)
    fechaHora = models.DateTimeField()
    contenido = models.CharField(max_length=500)
    def __str__(self):
                    return self.idUsuarioOrigen.__str__() + ": " + self.contenido