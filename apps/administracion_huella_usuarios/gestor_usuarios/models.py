from django.db import models
from apps.login.models import Usuarios
from django.contrib.auth.models import User
import sys



class Huella(models.Model):
    id_huella = models.AutoField(primary_key=True)
    datos_huella_dactilar = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # ELIMINA la línea que dice: id_usuario = models.ForeignKey(Usuarios, ...)
    
    # MANTÉN solo esta:
    usuario = models.ForeignKey(
    Usuarios,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)
    tiene_huella = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'huella'


# apps/administracion_huella_usuarios/gestor_usuarios/models.py

class registro_actividad(models.Model):
    id_registro_actividad = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(
        Usuarios, 
        on_delete=models.CASCADE, 
        db_column='id_usuario',
        null=True,
        blank=True
    )
    actividad = models.CharField(max_length=255)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    tipo_accion = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'registro_actividad'
        ordering = ['-fecha', '-hora']

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.id_usuario} - {self.tipo_accion}"



class HistorialFallos(models.Model):
    TIPO_FALLOS = [
        ('HUELLA_FALLIDA', 'Huella no coincide'),
        ('SIN_HUELLA', 'Usuario sin huella registrada'),
        ('LECTOR_ERROR', 'Error en el lector biométrico'),
        ('TIMEOUT', 'Tiempo excedido'),
        ('USUARIO_NO_EXISTE', 'Usuario no registrado en el sistema'),
    ]
    
    id_fallo = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True)
    tipo_fallo = models.CharField(max_length=50, choices=TIPO_FALLOS)
    cedula_intentada = models.CharField(max_length=191, null=True, blank=True)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    detalles = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'historial_fallos'
        ordering = ['-fecha', '-hora']
    
    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.get_tipo_fallo_display()} - {self.cedula_intentada or 'N/A'}"