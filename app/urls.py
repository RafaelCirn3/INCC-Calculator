from django.urls import path, include
from . import views


urlpatterns = [

#rota para a página inicial
    path('', views.base, name='home'),

#rota para o formulário de parcela
    path('calcular/', views.calcular_parcela, name='calcular_parcela'),

#rota para o openpyxl
    path('gerar_excel/', views.gerar_excel, name='gerar_excel'),

#rota do incc
    path('incc/', views.incc_index_form, name='incc_index'),

#rota de parcelas
    path('parcelas/', views.parcela_list, name='parcela_list'), 
    path('parcela/<int:parcela_id>/', views.parcela_detalhe, name='parcela_detalhe'),
    path('parcela_delete/<int:parcela_id>/', views.parcela_delete, name='parcela_delete'),
    path('parcelas/excluir-multiplas/', views.excluir_varias_parcelas, name='parcelas_excluir_multiplas'),

#rota para alimentar o incc
    path('alimentar_incc/', views.alimentar_incc, name='alimentar_incc'),
#rota da api
    path('api/', include('app.api.urls')),
]
