from django.utils import timezone
from django.db.models import Q

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
import re


# Create your forms here.

class FormNuevoUsuario(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirma tu contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'ciudad', 'edad', 'contacto')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")
        elif (not re.fullmatch(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$', password1)):
            raise ValidationError("La contraseña debe contener al menos un número, una letra minúscula,\n una letra mayúscula, un caracter especial (@$!%*#?&),\n tener una longitud de 8 caracteres y no contener espacios")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password2"])
        if commit:
            user.save()
        return user


class FormNuevoServUsuario(forms.ModelForm):
    OPTIONS = Categoria.objects.all()
    categorias = forms.ModelMultipleChoiceField(OPTIONS, required=False)

    class Meta:
        model = Servicio
        fields = ('nombre', 'descripcion', 'categorias')

    def presave(self, usuario, commit=True):
        servicio = super().save(commit=False)
        servicio.creacion = timezone.now()
        servicio.idUsuario = usuario
        if commit:
            servicio.save()
            servicio.categorias.add(*self.cleaned_data["categorias"])
        return servicio

class FormNuevoMensaje(forms.ModelForm):

    class Meta:
        model = Mensaje
        fields = ('contenido',)

    def save(self, conversacion, usuario1, usuario2, commit=True):
        mensaje = super().save(commit=False)
        mensaje.idUsuarioOrigen = usuario1
        mensaje.fechaHora = timezone.now()
        mensaje.idUsuarioDestino = usuario2
        mensaje.idConversacion = conversacion
        if commit:
            mensaje.save()
        return mensaje

class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'

class FormNuevoIntercambio(forms.ModelForm):
    inicio = forms.DateTimeField(widget=DateTimeInput)
    fin = forms.DateTimeField(widget=DateTimeInput)
    class Meta:
        model = Intercambio
        fields = ('inicio', 'fin')

    def validate(self, saldo):
        inicioForm = self.cleaned_data['inicio']
        finForm = self.cleaned_data['fin']
        if inicioForm < timezone.now():
            self.add_error('inicio', "La fecha no puede ser anterior al día de hoy")
            return False
        elif finForm < inicioForm:
            self.add_error('fin', "El fin no puede ser anterior al inicio")
            return False
        elif Intercambio.objects.filter(Q(inicio__range=[inicioForm, finForm]) | Q(fin__range=[inicioForm, finForm]) | Q(Q(inicio__lte=inicioForm) & Q(fin__gte=finForm)) | Q(Q(inicio__gte=inicioForm) & Q(fin__lte=finForm))).count()>=1:
            self.add_error('inicio', "Ya tiene un intercambio en este rango")
            return False
        elif int((finForm-inicioForm).total_seconds()//60)>saldo:
            self.add_error('inicio', "El tiempo del intercambio es superior a su saldo disponible")
            return False
        return True

    def save(self, servicio, usuarioRecibe, commit=True):
        intercambio = super().save(commit=False)
        intercambio.idUsuarioDa = servicio.idUsuario
        intercambio.idServicio = servicio
        intercambio.idUsuarioRecibe = usuarioRecibe
        if commit:
            intercambio.save()
        return intercambio

class FormBusqueda(forms.Form):
    descripcion = forms.CharField(max_length=500, required=False, label='Palabras clave')
    ciudad = forms.CharField(max_length=500, required=False)
    edad = forms.IntegerField(min_value=0, required=False)
    OPTIONS = Categoria.objects.all()
    categorias = forms.ModelMultipleChoiceField(OPTIONS, required=False)
    lista=(
        ("-creacion", "Ultimas publicaciones"),
        ("-nota", "Nota"),
        ("-idUsuario__last_login", "Última conexión del usuario"),
    )
    orden = forms.ChoiceField(choices=lista, label='Ordenar por:')

