from django.urls import path
from .views import webhook_huella
from . import views

app_name = 'gestor_usuarios'

urlpatterns = [
    path('', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('crear/', views.crear_usuario_view, name='crear_usuario'),
    path('carga-masiva/', views.carga_masiva_usuarios, name='carga_masiva'),
    path('editar/<int:id_usuario>/', views.editar_usuario_view, name='editar_usuario'),
    path('eliminar/<int:id_usuario>/', views.eliminar_usuario_view, name='eliminar'),
    path('cambiar-estado/<int:id_usuario>/', views.cambiar_estado_usuario_view, name='cambiar_estado'),
    path('huellas/', views.gestion_huellas, name='gestion_huellas'),
    path('huellas/eliminar/<int:id_usuario>/', views.eliminar_huella_usuario_view, name='eliminar_huella'),
    path('registro-actividad/', views.registro_actividad_view, name='registro_actividad'),
    path('historial-fallos/', views.historial_fallos, name='historial_fallos'),
    path('webhook/huella/', webhook_huella, name='webhook_huella'),
]