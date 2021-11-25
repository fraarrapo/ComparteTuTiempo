# Generated by Django 3.2.7 on 2021-11-25 17:23

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Conversacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('ciudad', models.CharField(max_length=100)),
                ('edad', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(200)])),
                ('contacto', models.CharField(blank=True, max_length=300)),
                ('saldo', models.PositiveIntegerField(default=30)),
                ('valoracion', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('descripcion', models.CharField(max_length=500, validators=[django.core.validators.MinLengthValidator(30)])),
                ('creacion', models.DateTimeField()),
                ('nota', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('estado', models.BooleanField(default=True)),
                ('categorias', models.ManyToManyField(blank=True, to='ComparteTuTiempoApp.Categoria')),
                ('idUsuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=300)),
                ('url', models.CharField(blank=True, max_length=200, null=True)),
                ('idUsuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Mensaje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechaHora', models.DateTimeField()),
                ('contenido', models.CharField(max_length=500)),
                ('idConversacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ComparteTuTiempoApp.conversacion')),
                ('idUsuarioDestino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='idUsuarioDestino', to=settings.AUTH_USER_MODEL)),
                ('idUsuarioOrigen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='idUsuarioOrigen', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Intercambio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicio', models.DateTimeField()),
                ('fin', models.DateTimeField()),
                ('confirmacion', models.PositiveIntegerField(default=0)),
                ('nota', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('idServicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ComparteTuTiempoApp.servicio')),
                ('idUsuarioDa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='idUsuarioDa', to=settings.AUTH_USER_MODEL)),
                ('idUsuarioRecibe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='idUsuarioRecibe', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='conversacion',
            name='idUsuario1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='idUsuario1', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='conversacion',
            name='idUsuario2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='idUsuario2', to=settings.AUTH_USER_MODEL),
        ),
    ]
