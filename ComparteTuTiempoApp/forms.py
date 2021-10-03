import datetime

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
    categorias = forms.ModelMultipleChoiceField(OPTIONS)

    class Meta:
        model = Servicio
        fields = ('nombre', 'descripcion', 'categorias')

    def presave(self, usuario, commit=True):
        servicio = super().save(commit=False)
        servicio.creacion = datetime.datetime.now()
        servicio.idUsuario = usuario
        if commit:
            servicio.save()
            servicio.categorias.add(*self.cleaned_data["categorias"])
        return servicio