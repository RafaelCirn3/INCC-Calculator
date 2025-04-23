from django.urls import path
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('calcular_parcela')),
    path('calcular/', views.calcular_parcela, name='calcular_parcela'),
    path('parcela/<int:parcela_id>/', views.parcela_detalhe, name='parcela_detalhe'),
    path('parcelas/', views.parcela_list, name='parcela_list'),  # 👈 nova rota
    path('gerar_excel/', views.gerar_excel, name='gerar_excel'),  # Nova URL para gerar o Excel


]
