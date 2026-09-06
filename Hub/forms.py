from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from Perfiles.models import Perfil


class UserForm(forms.ModelForm):
    """Alta de la cuenta: usuario y contraseña con las validaciones de Django."""

    password = forms.CharField(
        label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 8 caracteres. No puede ser solo numérica ni demasiado común.',
    )
    password_confirm = forms.CharField(
        label='Repite la contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ['username']
        labels = {'username': 'Nombre de usuario'}
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'})}

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('Ese nombre de usuario ya está en uso.')
        return username

    def clean(self):
        datos = super().clean()
        password = datos.get('password')
        confirmacion = datos.get('password_confirm')

        if password and confirmacion and password != confirmacion:
            self.add_error('password_confirm', 'Las contraseñas no coinciden.')
        elif password:
            try:
                validate_password(password, User(username=datos.get('username', '')))
            except ValidationError as e:
                self.add_error('password', e)
        return datos

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class NuevoPerfilForm(forms.ModelForm):
    """Datos personales mínimos para dar de alta a un paciente."""

    class Meta:
        model = Perfil
        fields = ['nombre', 'apellido', 'email', 'dni']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control',
                                             'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control',
                                             'placeholder': 'tu@email.com'}),
            'dni': forms.TextInput(attrs={'class': 'form-control',
                                          'placeholder': '12345678A'}),
        }

    def clean_dni(self):
        dni = self.cleaned_data['dni'].strip().upper()
        if Perfil.objects.filter(dni__iexact=dni).exists():
            raise ValidationError('Ya existe un perfil con ese DNI.')
        return dni

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if Perfil.objects.filter(email__iexact=email).exists():
            raise ValidationError('Ya existe un perfil con ese email.')
        return email
