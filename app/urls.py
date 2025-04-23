from django.urls import path
from django.shortcuts import redirect
from . import views


urlpatterns = [
    path('', lambda request: redirect('parcela_list'), name='home'),  # redireciona para a tela principal
    path('calcular/', views.calcular_parcela, name='calcular_parcela'),
    path('parcela/<int:parcela_id>/', views.parcela_detalhe, name='parcela_detalhe'),
    path('parcelas/', views.parcela_list, name='parcela_list'),  # ESTA é a tela que herda de base.html
    path('gerar_excel/', views.gerar_excel, name='gerar_excel'),
    path('incc/', views.incc_index_form, name='incc_create'),
]
