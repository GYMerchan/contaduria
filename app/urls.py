from django.urls import path
from .views import HomeView, AplicativoView, CuestionarioView, Tabla1, calcularTIR, Tabla3, CalcularValorRazonable, \
        Tabla2, Tabla4, Tabla5, Tabla6, Tabla7, Tabla8, Tabla9, Tabla10, Tabla11, Tabla12

urlpatterns = [
    path('', HomeView.as_view(), name='base'),
    path('aplicativo/', AplicativoView.as_view(), name='aplicativo'),
    path('aplicativo/tablas/', CuestionarioView.as_view(), name='tablas'),
    path('aplicativo/tir/', calcularTIR.as_view(), name='tir'),
    path('aplicativo/vp/', CalcularValorRazonable.as_view(), name='vp'),
    path('aplicativo/tablas/tabla1/', Tabla1.as_view(), name='tabla1'),
    path('aplicativo/tablas/tabla2/', Tabla2.as_view(), name='tabla2'),
    path('aplicativo/tablas/tabla3/', Tabla3.as_view(), name='tabla3'),
    path('aplicativo/tablas/tabla4/', Tabla4.as_view(), name='tabla4'),
    path('aplicativo/tablas/tabla5/', Tabla5.as_view(), name='tabla5'),
    path('aplicativo/tablas/tabla6/', Tabla6.as_view(), name='tabla6'),
    path('aplicativo/tablas/tabla7/', Tabla7.as_view(), name='tabla7'),
    path('aplicativo/tablas/tabla8/', Tabla8.as_view(), name='tabla8'),
    path('aplicativo/tablas/tabla9/', Tabla9.as_view(), name='tabla9'),
    path('aplicativo/tablas/tabla10/', Tabla10.as_view(), name='tabla10'),
    path('aplicativo/tablas/tabla11/', Tabla11.as_view(), name='tabla11'),
    path('aplicativo/tablas/tabla12/', Tabla12.as_view(), name='tabla12'),
    
]
