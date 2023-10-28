from django.urls import path
from .views import HomeView, AplicativoView, CuestionarioView, Tabla1, calcularTIR, Tabla3, CalcularValorRazonable, \
        Tabla2, Tabla4, Tabla5, Tabla6, Tabla7, Tabla8, Tabla9, Tabla10, Tabla11, Tabla12, BorrarConsulta, \
        HomeView2, AplicativoView2, CuestionarioView2, Tabla1c, Tabla2c, Tabla3c, Tabla4c, Tabla5c, Tabla6c, \
        Tabla7c, Tabla8c, Tabla9c, Tabla10c, Tabla11c, Tabla12c

urlpatterns = [
    path('', HomeView.as_view(), name='base'),
    path('aplicativo/borrar/', BorrarConsulta.as_view(), name='borrar'),
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
    path('base2/', HomeView2.as_view(), name='base2'),
    path('base2/aplicativo2/', AplicativoView2.as_view(), name='aplicativo2'),
    path('base2/aplicativo2/tablas2/', CuestionarioView2.as_view(), name='tablas2'),
    path('aplicativo2/tablas2/tabla1c/', Tabla1c.as_view(), name='tabla1c'),
    path('aplicativo2/tablas2/tabla2c/', Tabla2c.as_view(), name='tabla2c'),
    path('aplicativo2/tablas2/tabla3c/', Tabla3c.as_view(), name='tabla3c'),
    path('aplicativo2/tablas2/tabla4c/', Tabla4c.as_view(), name='tabla4c'),
    path('aplicativo2/tablas2/tabla5c', Tabla5c.as_view(), name='tabla5c'),
    path('aplicativo2/tablas2/tabla6c', Tabla6c.as_view(), name='tabla6c'),
    path('aplicativo2/tablas2/tabla7c', Tabla7c.as_view(), name='tabla7c'),
    path('aplicativo2/tablas2/tabla8c', Tabla8c.as_view(), name='tabla8c'),
    path('aplicativo2/tablas2/tabla9c', Tabla9c.as_view(), name='tabla9c'),
    path('aplicativo2/tablas2/tabla10c/', Tabla10c.as_view(), name='tabla10c'),
    path('aplicativo2/tablas2/tabla11c/', Tabla11c.as_view(), name='tabla11c'),
    path('aplicativo2/tablas2/tabla12c/', Tabla12c.as_view(), name='tabla12c'),






]
