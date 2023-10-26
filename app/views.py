from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.views import View
from django.shortcuts import render, redirect
from .forms import CalculoNIIF16Form
import numpy_financial as npf
from scipy.optimize import newton
import json
import numpy_financial as npf


# Create your views here.
class HomeView (TemplateView):
    template_name = 'app/base.html'

class BorrarConsulta (View):
    def post(self, request, *args, **kwargs):
        request.session.clear()
        return JsonResponse({'message': 'Datos borrados correctamente'})


class AplicativoView(View):
    template_name = 'app/aplicativo.html'
    
    def get(self, request):
        form = CalculoNIIF16Form()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CalculoNIIF16Form(request.POST)
        request.session.clear()
        if form.is_valid():
            valor_razonable = form.cleaned_data['valor_razonable']
            request.session['valor_razonable'] = valor_razonable
            if valor_razonable == 'si':
                canon = form.cleaned_data['canon_si']
                tiempo_arrendamiento = form.cleaned_data['tiempo_arrendamiento_si']
                vlr_razonable_tasa_implicita = form.cleaned_data['vlr_razonable_tasa_implicita_si']
                tasa_implicita_porcentaje = form.cleaned_data['tasa_implicita_porcentaje_si']
                tasa_implicita_porcentaje = float(tasa_implicita_porcentaje)
                tasa_implicita_porcentaje = round(tasa_implicita_porcentaje, 10)
                depreciacion_periodica = form.cleaned_data['depreciacion_periodica_si']

                impuesto_renta= 0.35
                diferido = vlr_razonable_tasa_implicita * impuesto_renta
                impuesto_diferido = int(diferido)
                request.session['impuesto_renta'] = impuesto_renta
                request.session['impuesto_diferido'] = impuesto_diferido
                request.session['canon'] = canon
                request.session['tiempo_arrendamiento'] = tiempo_arrendamiento
                request.session['vlr_razonable_tasa_implicita'] = vlr_razonable_tasa_implicita
                request.session['tasa_implicita_porcentaje'] = tasa_implicita_porcentaje
                request.session['depreciacion_periodica'] = depreciacion_periodica
            else:
                canon = form.cleaned_data['canon_no']
                tasa_implicita = form.cleaned_data['tasa_implicita_no']
                tasa_implicita = float(tasa_implicita)
                tiempo_arrendamiento = form.cleaned_data['tiempo_arrendamiento_no']
                valor_presente = form.cleaned_data['valor_presente_no']
                depreciacion_periodica = form.cleaned_data['depreciacion_periodica_no']
                #no seria necesario
                tasa_incremental = form.cleaned_data['tasa_incremental_no']
                tasa_incremental = float(tasa_incremental)

                impuesto_renta= 0.35
                diferido = valor_presente * impuesto_renta
                impuesto_diferido = int(diferido)
                request.session['impuesto_renta'] = impuesto_renta
                request.session['impuesto_diferido'] = impuesto_diferido
                request.session['canon'] = canon
                request.session['tasa_implicita'] = tasa_implicita
                request.session['tiempo_arrendamiento'] = tiempo_arrendamiento
                request.session['valor_presente'] = valor_presente
                request.session['depreciacion_periodica'] = depreciacion_periodica
                #no seria necesario
                request.session['tasa_incremental'] = tasa_incremental
            return redirect('tablas')
        return render(request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CalculoNIIF16Form()
        return context

class CalcularValorRazonable(View):
    def calcular_valor_razonable(self, canon, tiempo_arrendamiento, tir):
        valor_razonable = (canon * (1 - (1 + tir) ** (-tiempo_arrendamiento))) / tir
        return int(valor_razonable)
    
    def calcular_depreciacion(self, pago_canon, num_periodos, tir, valor_razonable_activo):
        vp_pagos_arrendamiento = npf.npv(rate=tir/100, values=[-pago_canon] * num_periodos)
        amortizacion_activo = valor_razonable_activo / num_periodos
        return int(amortizacion_activo)

    def post(self, request, *args, **kwargs):
        canon = float(request.POST.get('canon'))
        tiempo_arrendamiento = int(request.POST.get('tiempoArrendamiento'))
        tir = float(request.POST.get('tasaImplicta')) / 100.0
        valor_razonable_resultado = self.calcular_valor_razonable(canon, tiempo_arrendamiento, tir)
        amortizacion_activo = self.calcular_depreciacion(canon, tiempo_arrendamiento, tir, valor_razonable_resultado)
        resultados = {
            'valor_razonable': valor_razonable_resultado,
            'depreciacion': amortizacion_activo,
        }
        return JsonResponse(resultados)

class calcularTIR(View):
    def calcular_tir(self, pago_canon, num_periodos, valor_razonable_activo):
        tir = npf.irr([-valor_razonable_activo] + [pago_canon] * num_periodos)
        return tir

    def calcular_depreciacion(self, pago_canon, num_periodos, valor_razonable_activo, tir):
        vp_pagos_arrendamiento = npf.npv(rate=tir/100, values=[-pago_canon] * num_periodos)
        amortizacion_activo = valor_razonable_activo / num_periodos
        return int(amortizacion_activo)

    def post(self, request, *args, **kwargs):
        pago_canon = int(request.POST.get('canon'))
        num_periodos = int(request.POST.get('tiempoArrendamiento'))
        valor_razonable_activo = int(request.POST.get('valorRazonable'))
        tir_result = self.calcular_tir(pago_canon, num_periodos, valor_razonable_activo)
        amortizacion_activo = self.calcular_depreciacion(pago_canon, num_periodos, valor_razonable_activo, tir_result)
        tir_resulta = tir_result*100
        tir_resultado = round(tir_resulta, 10)

        resultados = {
            'tir': tir_resultado,
            'depreciacion': amortizacion_activo
        }
        return JsonResponse(resultados)
    
class CuestionarioView (TemplateView):
    template_name = 'app/tablas.html'

class Tabla1 (TemplateView):
    template_name = 'app/tabla1.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        canon = self.request.session.get('canon', 0)
        valor_razonable = self.request.session.get('valor_razonable', 0)
        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            saldo_actual = vlr_razonable_tasa_implicita
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                amortizacion_data.append({
                    'periodo': periodo,
                    'cuota': canon,
                    'interes': interes,
                    'amortizacion': amortizacion,
                    'saldo': saldo_actual
                })
            context['activo_uso'] = vlr_razonable_tasa_implicita
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            saldo_actual = valor_presente
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita/100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                amortizacion_data.append({
                    'periodo': periodo,
                    'cuota': canon,
                    'interes': interes,
                    'amortizacion': amortizacion,
                    'saldo': saldo_actual
                })
            context['activo_uso'] = valor_presente
        context['amortizacion_data'] = amortizacion_data
        context['canon'] = canon
        return context

class Tabla2(TemplateView):
    template_name = 'app/tabla2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        impuesto_renta = self.request.session.get('impuesto_renta', 0)
        impuesto_renta = float(impuesto_renta*100)
        impuesto_diferido = self.request.session.get('impuesto_diferido', 0)
        valor_razonable = self.request.session.get('valor_razonable', 0)
        if valor_razonable == 'si':
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            context['activo_uso'] = vlr_razonable_tasa_implicita

        else:
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            context['activo_uso'] = valor_presente
        context['impuesto_renta'] = impuesto_renta
        context['impuesto_diferido'] = impuesto_diferido
        return context

class Tabla3 (TemplateView):
    template_name = 'app/tabla3.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        depreciaciones = self.request.session.get('depreciacion_periodica', [])
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        context['periodos_lista'] = periodos_lista
        context['depreciaciones'] = depreciaciones
        return context

class Tabla4 (TemplateView):
    template_name = 'app/tabla4.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        canon = self.request.session.get('canon', 0)
        valor_razonable = self.request.session.get('valor_razonable', 0)
        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            saldo_actual = vlr_razonable_tasa_implicita
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                amortizacion_data.append({
                    'periodo': periodo,
                    'cuota': canon,
                    'interes': interes,
                    'amortizacion': amortizacion,
                    'saldo': saldo_actual
                })
            context['activo_uso'] = vlr_razonable_tasa_implicita
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            saldo_actual = valor_presente
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita/100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                amortizacion_data.append({
                    'periodo': periodo,
                    'cuota': canon,
                    'interes': interes,
                    'amortizacion': amortizacion,
                    'saldo': saldo_actual
                })
            context['activo_uso'] = valor_presente
        context['amortizacion_data'] = amortizacion_data
        context['canon'] = canon
        return context           

class Tabla5 (TemplateView):
    template_name = 'app/tabla5.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        canon = self.request.session.get('canon', 0)
        valor_razonable = self.request.session.get('valor_razonable', 0)
        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            saldo_actual = vlr_razonable_tasa_implicita
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                amortizacion_data.append({
                    'periodo': periodo,
                    'cuota': canon,
                    'interes': interes,
                    'amortizacion': amortizacion,
                    'saldo': saldo_actual
                })
            context['activo_uso'] = vlr_razonable_tasa_implicita
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            saldo_actual = valor_presente
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita/100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                amortizacion_data.append({
                    'periodo': periodo,
                    'cuota': canon,
                    'interes': interes,
                    'amortizacion': amortizacion,
                    'saldo': saldo_actual
                })
            context['activo_uso'] = valor_presente
        context['amortizacion_data'] = amortizacion_data
        context['canon'] = canon
        return context           
    
class Tabla6(TemplateView):
    template_name = 'app/tabla6.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        canon = self.request.session.get('canon', 0)
        depreciacion = self.request.session.get('depreciacion_periodica', 0)
        impuesto_renta = self.request.session.get('impuesto_renta', 0)
        impuesto_diferido_1 = self.request.session.get('impuesto_diferido', 0)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        valor_razonable = self.request.session.get('valor_razonable', 0)

        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            valor_activo = vlr_razonable_tasa_implicita
            valor_pasivo = vlr_razonable_tasa_implicita
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = valor_pasivo * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                saldo_neto_activo = valor_activo - depreciacion
                saldo_neto_pasivo = valor_pasivo - amortizacion
                impuesto_diferido_activo = saldo_neto_activo * (impuesto_renta / 100)
                impuesto_diferido_pasivo = saldo_neto_pasivo * (impuesto_renta / 100)
                dif_temp_neta = saldo_neto_activo - saldo_neto_pasivo
                dif_imp_dif_neto = impuesto_diferido_activo - impuesto_diferido_pasivo
                amortizacion_data.append({
                    'periodo': periodo,
                    'valor_activo': valor_activo,
                    'valor_pasivo': valor_pasivo,
                    'saldo_neto_activo': saldo_neto_activo,
                    'saldo_neto_pasivo': saldo_neto_pasivo,
                    'impuesto_diferido_activo': (impuesto_diferido_activo*100),
                    'impuesto_diferido_pasivo': (impuesto_diferido_pasivo*100),
                    'amortizacion': amortizacion,
                    'depreciacion': depreciacion,
                    'dif_temp_neta': dif_temp_neta,
                    'dif_imp_dif_neto': (dif_imp_dif_neto *100),
                })
                valor_activo = saldo_neto_activo
                valor_pasivo = saldo_neto_pasivo
            context['activo_uso'] = vlr_razonable_tasa_implicita
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            valor_activo = valor_presente
            valor_pasivo = valor_presente
            amortizacion= 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = valor_pasivo * (tasa_implicita/100)
                amortizacion = canon - interes
                saldo_neto_activo = valor_activo - depreciacion
                saldo_neto_pasivo = valor_pasivo - amortizacion
                impuesto_diferido_activo = saldo_neto_activo * (impuesto_renta / 100)
                impuesto_diferido_pasivo = saldo_neto_pasivo * (impuesto_renta / 100)
                dif_temp_neta = saldo_neto_activo - saldo_neto_pasivo
                dif_imp_dif_neto = impuesto_diferido_activo - impuesto_diferido_pasivo
                amortizacion_data.append({
                    'periodo': periodo,
                    'valor_activo': valor_activo,
                    'valor_pasivo': valor_pasivo,
                    'saldo_neto_activo': saldo_neto_activo,
                    'saldo_neto_pasivo': saldo_neto_pasivo,
                    'impuesto_diferido_activo': (impuesto_diferido_activo*100),
                    'impuesto_diferido_pasivo': (impuesto_diferido_pasivo*100),
                    'amortizacion': amortizacion,
                    'depreciacion': depreciacion,
                    'dif_temp_neta': dif_temp_neta,
                    'dif_imp_dif_neto': (dif_imp_dif_neto *100),
                })
                valor_activo = saldo_neto_activo
                valor_pasivo = saldo_neto_pasivo

            context['activo_uso'] = valor_presente
        context['amortizacion_data'] = amortizacion_data
        self.request.session['amortizacion_data'] = amortizacion_data
        context['impuesto_diferido_1'] = impuesto_diferido_1
        return context
    
class Tabla7(TemplateView):
    template_name = 'app/tabla7.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        canon = self.request.session.get('canon', 0)
        depreciacion = self.request.session.get('depreciacion_periodica', 0)
        impuesto_renta = self.request.session.get('impuesto_renta', 0)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        valor_razonable = self.request.session.get('valor_razonable', 0)

        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            saldo_actual = vlr_razonable_tasa_implicita
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                saldo_actual -= amortizacion
                interes = saldo_actual * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                total = interes + depreciacion
                dif_temporal = total - canon
                imp_diferido = dif_temporal * (impuesto_renta / 100)
                amortizacion_data.append({
                    'periodo': periodo,
                    'interes': interes,
                    'depreciacion': depreciacion,
                    'total': total,
                    'canon': canon,
                    'dif_temporal': dif_temporal,
                    'imp_diferido': (imp_diferido*100),
                })
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            saldo_actual = valor_presente
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                saldo_actual -= amortizacion
                interes = saldo_actual * (tasa_implicita/100)
                amortizacion = canon - interes
                total = interes + depreciacion
                dif_temporal = total - canon
                imp_diferido = dif_temporal * (impuesto_renta / 100)
                amortizacion_data.append({
                    'periodo': periodo,
                    'interes': interes,
                    'depreciacion': depreciacion,
                    'total': total,
                    'canon': canon,
                    'dif_temporal': dif_temporal,
                    'imp_diferido': (imp_diferido*100),
                })
        context['amortizacion_data'] = amortizacion_data
        return context

class Tabla8(TemplateView):
    template_name = 'app/tabla8.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        canon = self.request.session.get('canon', 0)
        depreciacion = self.request.session.get('depreciacion_periodica', 0)
        impuesto_renta = self.request.session.get('impuesto_renta', 0)
        impuesto_diferido_1 = self.request.session.get('impuesto_diferido', 0)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        valor_razonable = self.request.session.get('valor_razonable', 0)

        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            #pasivo
            valor_pasivo = vlr_razonable_tasa_implicita
            impuesto_pasivo_anterior = (impuesto_diferido_1/100)
            amortizacion = 0
            #activo
            valor_activo = vlr_razonable_tasa_implicita
            impuesto_activo_anterior = (impuesto_diferido_1/100)

            dif_imp_dif_neto_anterior=0
            amortizacion_data = []
            for periodo in periodos_lista:
                #pasivo
                interes = valor_pasivo * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                saldo_neto_pasivo = valor_pasivo - amortizacion
                impuesto_diferido_pasivo = saldo_neto_pasivo * (impuesto_renta / 100)
                impuesto_pasivo = impuesto_pasivo_anterior - impuesto_diferido_pasivo
                #activo
                saldo_neto_activo = valor_activo - depreciacion
                impuesto_diferido_activo = saldo_neto_activo * (impuesto_renta / 100)
                impuesto_activo = impuesto_activo_anterior -impuesto_diferido_activo

                dif_imp_dif_neto = impuesto_diferido_activo - impuesto_diferido_pasivo
                diferencia_diferencia = dif_imp_dif_neto_anterior - dif_imp_dif_neto
                amortizacion_data.append({
                    #pasivo
                    'periodo': periodo,
                    'impuesto_pasivo': (impuesto_pasivo * 100),
                    #activo
                    'periodo': periodo,
                    'impuesto_activo': (impuesto_activo * 100),

                    'dif_imp_dif_neto': (dif_imp_dif_neto * 100),
                    'diferencia_diferencia': (diferencia_diferencia * 100),

                })
                #pasivo
                valor_pasivo = saldo_neto_pasivo
                impuesto_pasivo_anterior = impuesto_diferido_pasivo
                #activo
                impuesto_activo_anterior = impuesto_diferido_activo
                valor_activo = saldo_neto_activo

                dif_imp_dif_neto_anterior = dif_imp_dif_neto
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            #pasivo
            valor_pasivo = valor_presente
            impuesto_pasivo_anterior = (impuesto_diferido_1/100)
            amortizacion = 0
            #activo
            valor_activo = valor_presente
            impuesto_activo_anterior = (impuesto_diferido_1/100)

            dif_imp_dif_neto_anterior=0
            amortizacion_data = []
            amortizacion_data = []
            for periodo in periodos_lista:
                #pasivo
                interes = valor_pasivo * (tasa_implicita / 100)
                amortizacion = canon - interes
                saldo_neto_pasivo = valor_pasivo - amortizacion
                impuesto_diferido_pasivo = saldo_neto_pasivo * (impuesto_renta / 100)
                impuesto_pasivo = impuesto_pasivo_anterior - impuesto_diferido_pasivo
                #activo
                saldo_neto_activo = valor_activo - depreciacion
                impuesto_diferido_activo = saldo_neto_activo * (impuesto_renta / 100)
                impuesto_activo = impuesto_activo_anterior -impuesto_diferido_activo

                dif_imp_dif_neto = impuesto_diferido_activo - impuesto_diferido_pasivo
                diferencia_diferencia = dif_imp_dif_neto_anterior - dif_imp_dif_neto
                amortizacion_data.append({
                    #pasivo
                    'periodo': periodo,
                    'impuesto_pasivo': (impuesto_pasivo * 100),
                    #activo
                    'periodo': periodo,
                    'impuesto_activo': (impuesto_activo * 100),

                    'dif_imp_dif_neto': (dif_imp_dif_neto * 100),
                    'diferencia_diferencia': (diferencia_diferencia * 100),

                })
                #pasivo
                valor_pasivo = saldo_neto_pasivo
                impuesto_pasivo_anterior = impuesto_diferido_pasivo
                #activo
                impuesto_activo_anterior = impuesto_diferido_activo
                valor_activo = saldo_neto_activo

                dif_imp_dif_neto_anterior = dif_imp_dif_neto
            context['activo_uso'] = valor_presente
        context['amortizacion_data'] = amortizacion_data
        context['impuesto_diferido_1'] = impuesto_diferido_1
        return context
    
class Tabla9(TemplateView):
    template_name = 'app/tabla9.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        depreciacion = self.request.session.get('depreciacion_periodica', 0)
        impuesto_renta = self.request.session.get('impuesto_renta', 0)
        canon = self.request.session.get('canon', 0)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        impuesto_renta = float(impuesto_renta*100)
        impuesto_diferido = self.request.session.get('impuesto_diferido', 0)
        valor_razonable = self.request.session.get('valor_razonable', 0)
        #prueba
        efectivo = canon * periodos
        efectivo_sit_financiera = -efectivo
        impuesto_diferido_sit_financiera = impuesto_diferido - impuesto_diferido
        #estado
        impuesto_diferido_1 = impuesto_diferido
        #pasivo
        impuesto_pasivo_anterior = (impuesto_diferido_1/100)
        amortizacion = 0
        #activo
        impuesto_activo_anterior = (impuesto_diferido_1/100)

        dif_imp_dif_neto_anterior=0
        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            #Balance prueba
            total_activo= efectivo_sit_financiera + vlr_razonable_tasa_implicita + (-vlr_razonable_tasa_implicita)
            pasivo_arrendamiento = vlr_razonable_tasa_implicita - efectivo
            total_pasivo= pasivo_arrendamiento + impuesto_diferido_sit_financiera
            comprobacion_debe = vlr_razonable_tasa_implicita + impuesto_diferido + vlr_razonable_tasa_implicita + impuesto_diferido + efectivo
            comprobacion_haber = efectivo + impuesto_diferido + vlr_razonable_tasa_implicita + efectivo + impuesto_diferido
            comprobacion = total_activo + total_pasivo
            context['activo_uso'] = vlr_razonable_tasa_implicita
            context['amortizacion'] = vlr_razonable_tasa_implicita
            context['amortizacion_sit_financiera'] = -vlr_razonable_tasa_implicita
            context['total_activo'] = total_activo
            context['pasivo_arrendamiento'] = pasivo_arrendamiento
            context['total_pasivo'] = total_pasivo
            context['comprobacion_debe'] = comprobacion_debe
            context['comprobacion_haber'] = comprobacion_haber
            context['comprobacion'] = comprobacion
            #Estado
            utilidad_bruta=0
            context['utilidad_bruta'] = utilidad_bruta

            #pasivo
            valor_pasivo = vlr_razonable_tasa_implicita
            impuesto_pasivo_anterior = (impuesto_diferido_1)
            amortizacion = 0

            #activo
            valor_activo = vlr_razonable_tasa_implicita
            impuesto_activo_anterior = (impuesto_diferido_1)

            dif_imp_dif_neto_anterior=0
            total_impuestos_activos = 0
            total_impuestos_pasivos = 0
            gasto_financiero= 0
            for periodo in periodos_lista:
                #pasivo
                interes = valor_pasivo * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                saldo_neto_pasivo = valor_pasivo - amortizacion
                impuesto_diferido_pasivo = saldo_neto_pasivo * (impuesto_renta / 100)
                impuesto_pasivo = impuesto_pasivo_anterior - impuesto_diferido_pasivo
                total_impuestos_pasivos  += impuesto_pasivo
                imp_pasivo = impuesto_diferido + total_impuestos_pasivos
                context['imp_pasivo'] = imp_pasivo
                context['total_impuestos_pasivos'] = total_impuestos_pasivos
                #activo
                saldo_neto_activo = valor_activo - depreciacion
                impuesto_diferido_activo = saldo_neto_activo * (impuesto_renta / 100)
                impuesto_activo = impuesto_activo_anterior -impuesto_diferido_activo
                total_impuestos_activos  += impuesto_activo
                imp_activo= impuesto_diferido + total_impuestos_activos
                dif_imp_dif_neto = impuesto_diferido_activo - impuesto_diferido_pasivo
                diferencia_diferencia = dif_imp_dif_neto_anterior - dif_imp_dif_neto
                context['imp_activo'] = imp_activo
                
                gastos_total = imp_activo - imp_pasivo
                activo_uso = vlr_razonable_tasa_implicita
                utilidad_operacion = utilidad_bruta + gastos_total - activo_uso

                gasto_financiero += interes
                utilidad_antes_impuestos = utilidad_operacion - gasto_financiero
                impuestos=0
                suma_debe = imp_activo + activo_uso + gasto_financiero
                suma_haber = imp_pasivo
                utilidad_neta = utilidad_antes_impuestos - impuestos
                perdida_total = utilidad_neta
                if suma_debe > suma_haber:
                    perdida_debe = suma_debe - suma_haber
                    context['perdida_debe'] = perdida_debe
                else:
                    perdida_haber =  suma_haber - suma_debe
                    context['perdida_haber'] = perdida_haber

                context['gastos_total'] = gastos_total
                context['utilidad_operacion'] = utilidad_operacion
                context['gasto_financiero'] = gasto_financiero
                context['utilidad_antes_impuestos'] = utilidad_antes_impuestos
                context['impuestos'] = impuestos
                context['utilidad_neta'] = utilidad_neta
                context['suma_debe'] = suma_debe
                context['suma_haber'] = suma_haber
                context['perdida_total'] = perdida_total


                #pasivo
                valor_pasivo = saldo_neto_pasivo
                impuesto_pasivo_anterior = impuesto_diferido_pasivo
                #activo
                impuesto_activo_anterior = impuesto_diferido_activo
                valor_activo = saldo_neto_activo

        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            #Balance prueba
            total_activo= efectivo_sit_financiera + valor_presente + (-valor_presente)
            pasivo_arrendamiento = valor_presente - efectivo
            total_pasivo= pasivo_arrendamiento + impuesto_diferido_sit_financiera
            comprobacion_debe = valor_presente + impuesto_diferido + valor_presente + impuesto_diferido + efectivo
            comprobacion_haber = efectivo + impuesto_diferido + valor_presente + efectivo + impuesto_diferido
            comprobacion = total_activo + total_pasivo
            context['activo_uso'] = valor_presente
            context['amortizacion'] = valor_presente
            context['amortizacion_sit_financiera'] = -valor_presente
            context['total_activo'] = total_activo
            context['pasivo_arrendamiento'] = pasivo_arrendamiento
            context['total_pasivo'] = total_pasivo
            context['comprobacion_debe'] = comprobacion_debe
            context['comprobacion_haber'] = comprobacion_haber
            context['comprobacion'] = comprobacion
            #Estado
            utilidad_bruta=0
            context['utilidad_bruta'] = utilidad_bruta

            #pasivo
            valor_pasivo = valor_presente
            impuesto_pasivo_anterior = (impuesto_diferido_1)
            amortizacion = 0

            #activo
            valor_activo = valor_presente
            impuesto_activo_anterior = (impuesto_diferido_1)

            dif_imp_dif_neto_anterior=0
            total_impuestos_activos = 0
            total_impuestos_pasivos = 0
            gasto_financiero= 0
            for periodo in periodos_lista:
                #pasivo
                interes = valor_pasivo * (tasa_implicita / 100)
                amortizacion = canon - interes
                saldo_neto_pasivo = valor_pasivo - amortizacion
                impuesto_diferido_pasivo = saldo_neto_pasivo * (impuesto_renta / 100)
                impuesto_pasivo = impuesto_pasivo_anterior - impuesto_diferido_pasivo
                total_impuestos_pasivos  += impuesto_pasivo
                imp_pasivo = impuesto_diferido + total_impuestos_pasivos
                context['imp_pasivo'] = imp_pasivo
                context['total_impuestos_pasivos'] = total_impuestos_pasivos
                #activo
                saldo_neto_activo = valor_activo - depreciacion
                impuesto_diferido_activo = saldo_neto_activo * (impuesto_renta / 100)
                impuesto_activo = impuesto_activo_anterior -impuesto_diferido_activo
                total_impuestos_activos  += impuesto_activo
                imp_activo= impuesto_diferido + total_impuestos_activos
                dif_imp_dif_neto = impuesto_diferido_activo - impuesto_diferido_pasivo
                diferencia_diferencia = dif_imp_dif_neto_anterior - dif_imp_dif_neto
                context['imp_activo'] = imp_activo
                
                gastos_total = imp_activo - imp_pasivo
                activo_uso = valor_presente
                utilidad_operacion = utilidad_bruta + gastos_total - activo_uso

                gasto_financiero += interes
                utilidad_antes_impuestos = utilidad_operacion - gasto_financiero
                impuestos=0
                suma_debe = imp_activo + activo_uso + gasto_financiero
                suma_haber = imp_pasivo
                utilidad_neta = utilidad_antes_impuestos - impuestos
                perdida_total = utilidad_neta
                if suma_debe > suma_haber:
                    perdida_debe = suma_debe - suma_haber
                    context['perdida_debe'] = perdida_debe
                else:
                    perdida_haber =  suma_haber - suma_debe
                    context['perdida_haber'] = perdida_haber

                context['gastos_total'] = gastos_total
                context['utilidad_operacion'] = utilidad_operacion
                context['gasto_financiero'] = gasto_financiero
                context['utilidad_antes_impuestos'] = utilidad_antes_impuestos
                context['impuestos'] = impuestos
                context['utilidad_neta'] = utilidad_neta
                context['suma_debe'] = suma_debe
                context['suma_haber'] = suma_haber
                context['perdida_total'] = perdida_total


                #pasivo
                valor_pasivo = saldo_neto_pasivo
                impuesto_pasivo_anterior = impuesto_diferido_pasivo
                #activo
                impuesto_activo_anterior = impuesto_diferido_activo
                valor_activo = saldo_neto_activo

        context['impuesto_renta'] = impuesto_renta
        context['efectivo'] = efectivo
        context['efectivo_sit_financiera'] = efectivo_sit_financiera
        context['impuesto_diferido'] = impuesto_diferido
        context['impuesto_diferido_sit_financiera'] = impuesto_diferido_sit_financiera
        return context
    
class Tabla10 (TemplateView):
    template_name = 'app/tabla10.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        canon = self.request.session.get('canon', 0)
        depreciacion = self.request.session.get('depreciacion_periodica', 0)
        impuesto_renta = self.request.session.get('impuesto_renta', 0)
        impuesto_renta = float(impuesto_renta*100)
        valor_razonable = self.request.session.get('valor_razonable', 0)
        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            saldo_actual = vlr_razonable_tasa_implicita
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita_porcentaje/100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                total = interes + depreciacion
                diferencia = total - canon
                impuesto_diferencia = diferencia * (impuesto_renta/100)
                amortizacion_data.append({
                    'periodo': periodo,
                    'canon': canon,
                    'interes': interes,
                    'depreciacion': depreciacion,
                    'total': total,
                    'diferencia': diferencia,
                    'impuesto_diferencia': impuesto_diferencia,
                })
            context['activo_uso'] = vlr_razonable_tasa_implicita
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            saldo_actual = valor_presente
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita/100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                total = interes + depreciacion
                diferencia = total - canon
                impuesto_diferencia = diferencia * (impuesto_renta/100)
                amortizacion_data.append({
                    'periodo': periodo,
                    'canon': canon,
                    'interes': interes,
                    'depreciacion': depreciacion,
                    'total': total,
                    'diferencia': diferencia,
                    'impuesto_diferencia': impuesto_diferencia,
                })
            context['activo_uso'] = valor_presente
        context['amortizacion_data'] = amortizacion_data
        context['canon'] = canon
        return context 
    
class Tabla11 (TemplateView):
    template_name = 'app/tabla11.html'

class Tabla12 (TemplateView):
    template_name = 'app/tabla12.html'







#modo claro


class HomeView2 (TemplateView):
    template_name = 'app/base2.html'

class BorrarConsulta (View):
    def post(self, request, *args, **kwargs):
        request.session.clear()
        return JsonResponse({'message': 'Datos borrados correctamente'})

class AplicativoView2(View):
    template_name = 'app/aplicativo2.html'
    
    def get(self, request):
        form = CalculoNIIF16Form()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CalculoNIIF16Form(request.POST)
        request.session.clear()
        if form.is_valid():
            valor_razonable = form.cleaned_data['valor_razonable']
            request.session['valor_razonable'] = valor_razonable
            if valor_razonable == 'si':
                canon = form.cleaned_data['canon_si']
                tiempo_arrendamiento = form.cleaned_data['tiempo_arrendamiento_si']
                vlr_razonable_tasa_implicita = form.cleaned_data['vlr_razonable_tasa_implicita_si']
                tasa_implicita_porcentaje = form.cleaned_data['tasa_implicita_porcentaje_si']
                tasa_implicita_porcentaje = float(tasa_implicita_porcentaje)
                tasa_implicita_porcentaje = round(tasa_implicita_porcentaje, 10)
                depreciacion_periodica = form.cleaned_data['depreciacion_periodica_si']

                impuesto_renta= 0.35
                diferido = vlr_razonable_tasa_implicita * impuesto_renta
                impuesto_diferido = int(diferido)
                request.session['impuesto_renta'] = impuesto_renta
                request.session['impuesto_diferido'] = impuesto_diferido
                request.session['canon'] = canon
                request.session['tiempo_arrendamiento'] = tiempo_arrendamiento
                request.session['vlr_razonable_tasa_implicita'] = vlr_razonable_tasa_implicita
                request.session['tasa_implicita_porcentaje'] = tasa_implicita_porcentaje
                request.session['depreciacion_periodica'] = depreciacion_periodica
            else:
                canon = form.cleaned_data['canon_no']
                tasa_implicita = form.cleaned_data['tasa_implicita_no']
                tasa_implicita = float(tasa_implicita)
                tiempo_arrendamiento = form.cleaned_data['tiempo_arrendamiento_no']
                valor_presente = form.cleaned_data['valor_presente_no']
                depreciacion_periodica = form.cleaned_data['depreciacion_periodica_no']
                #no seria necesario
                tasa_incremental = form.cleaned_data['tasa_incremental_no']
                tasa_incremental = float(tasa_incremental)

                impuesto_renta= 0.35
                diferido = valor_presente * impuesto_renta
                impuesto_diferido = int(diferido)
                request.session['impuesto_renta'] = impuesto_renta
                request.session['impuesto_diferido'] = impuesto_diferido
                request.session['canon'] = canon
                request.session['tasa_implicita'] = tasa_implicita
                request.session['tiempo_arrendamiento'] = tiempo_arrendamiento
                request.session['valor_presente'] = valor_presente
                request.session['depreciacion_periodica'] = depreciacion_periodica
                #no seria necesario
                request.session['tasa_incremental'] = tasa_incremental
            return redirect('tablas2')
        return render(request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CalculoNIIF16Form()
        return context

class CalcularValorRazonable(View):
    def calcular_valor_razonable(self, canon, tiempo_arrendamiento, tir):
        valor_razonable = (canon * (1 - (1 + tir) ** (-tiempo_arrendamiento))) / tir
        return int(valor_razonable)
    
    def calcular_depreciacion(self, pago_canon, num_periodos, tir, valor_razonable_activo):
        vp_pagos_arrendamiento = npf.npv(rate=tir/100, values=[-pago_canon] * num_periodos)
        amortizacion_activo = valor_razonable_activo / num_periodos
        return int(amortizacion_activo)

    def post(self, request, *args, **kwargs):
        canon = float(request.POST.get('canon'))
        tiempo_arrendamiento = int(request.POST.get('tiempoArrendamiento'))
        tir = float(request.POST.get('tasaImplicta')) / 100.0
        valor_razonable_resultado = self.calcular_valor_razonable(canon, tiempo_arrendamiento, tir)
        amortizacion_activo = self.calcular_depreciacion(canon, tiempo_arrendamiento, tir, valor_razonable_resultado)
        resultados = {
            'valor_razonable': valor_razonable_resultado,
            'depreciacion': amortizacion_activo,
        }
        return JsonResponse(resultados)

class calcularTIR(View):
    def calcular_tir(self, pago_canon, num_periodos, valor_razonable_activo):
        tir = npf.irr([-valor_razonable_activo] + [pago_canon] * num_periodos)
        return tir

    def calcular_depreciacion(self, pago_canon, num_periodos, valor_razonable_activo, tir):
        vp_pagos_arrendamiento = npf.npv(rate=tir/100, values=[-pago_canon] * num_periodos)
        amortizacion_activo = valor_razonable_activo / num_periodos
        return int(amortizacion_activo)

    def post(self, request, *args, **kwargs):
        pago_canon = int(request.POST.get('canon'))
        num_periodos = int(request.POST.get('tiempoArrendamiento'))
        valor_razonable_activo = int(request.POST.get('valorRazonable'))
        tir_result = self.calcular_tir(pago_canon, num_periodos, valor_razonable_activo)
        amortizacion_activo = self.calcular_depreciacion(pago_canon, num_periodos, valor_razonable_activo, tir_result)
        tir_resulta = tir_result*100
        tir_resultado = round(tir_resulta, 10)

        resultados = {
            'tir': tir_resultado,
            'depreciacion': amortizacion_activo
        }
        return JsonResponse(resultados)
    
class CuestionarioView2 (TemplateView):
    template_name = 'app/tablas2.html'

class Tabla1c (TemplateView):
    template_name = 'app/tabla1c.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        canon = self.request.session.get('canon', 0)
        valor_razonable = self.request.session.get('valor_razonable', 0)
        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            saldo_actual = vlr_razonable_tasa_implicita
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                amortizacion_data.append({
                    'periodo': periodo,
                    'cuota': canon,
                    'interes': interes,
                    'amortizacion': amortizacion,
                    'saldo': saldo_actual
                })
            context['activo_uso'] = vlr_razonable_tasa_implicita
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            saldo_actual = valor_presente
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita/100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                amortizacion_data.append({
                    'periodo': periodo,
                    'cuota': canon,
                    'interes': interes,
                    'amortizacion': amortizacion,
                    'saldo': saldo_actual
                })
            context['activo_uso'] = valor_presente
        context['amortizacion_data'] = amortizacion_data
        context['canon'] = canon
        return context

class Tabla2c(TemplateView):
    template_name = 'app/tabla2c.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        impuesto_renta = self.request.session.get('impuesto_renta', 0)
        impuesto_renta = float(impuesto_renta*100)
        impuesto_diferido = self.request.session.get('impuesto_diferido', 0)
        valor_razonable = self.request.session.get('valor_razonable', 0)
        if valor_razonable == 'si':
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            context['activo_uso'] = vlr_razonable_tasa_implicita

        else:
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            context['activo_uso'] = valor_presente
        context['impuesto_renta'] = impuesto_renta
        context['impuesto_diferido'] = impuesto_diferido
        return context

class Tabla3 (TemplateView):
    template_name = 'app/tabla3.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        depreciaciones = self.request.session.get('depreciacion_periodica', [])
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        context['periodos_lista'] = periodos_lista
        context['depreciaciones'] = depreciaciones
        return context

class Tabla4 (TemplateView):
    template_name = 'app/tabla4.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        canon = self.request.session.get('canon', 0)
        valor_razonable = self.request.session.get('valor_razonable', 0)
        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            saldo_actual = vlr_razonable_tasa_implicita
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                amortizacion_data.append({
                    'periodo': periodo,
                    'cuota': canon,
                    'interes': interes,
                    'amortizacion': amortizacion,
                    'saldo': saldo_actual
                })
            context['activo_uso'] = vlr_razonable_tasa_implicita
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            saldo_actual = valor_presente
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita/100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                amortizacion_data.append({
                    'periodo': periodo,
                    'cuota': canon,
                    'interes': interes,
                    'amortizacion': amortizacion,
                    'saldo': saldo_actual
                })
            context['activo_uso'] = valor_presente
        context['amortizacion_data'] = amortizacion_data
        context['canon'] = canon
        return context           

class Tabla5 (TemplateView):
    template_name = 'app/tabla5.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        canon = self.request.session.get('canon', 0)
        valor_razonable = self.request.session.get('valor_razonable', 0)
        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            saldo_actual = vlr_razonable_tasa_implicita
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                amortizacion_data.append({
                    'periodo': periodo,
                    'cuota': canon,
                    'interes': interes,
                    'amortizacion': amortizacion,
                    'saldo': saldo_actual
                })
            context['activo_uso'] = vlr_razonable_tasa_implicita
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            saldo_actual = valor_presente
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita/100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                amortizacion_data.append({
                    'periodo': periodo,
                    'cuota': canon,
                    'interes': interes,
                    'amortizacion': amortizacion,
                    'saldo': saldo_actual
                })
            context['activo_uso'] = valor_presente
        context['amortizacion_data'] = amortizacion_data
        context['canon'] = canon
        return context           
    
class Tabla6(TemplateView):
    template_name = 'app/tabla6.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        canon = self.request.session.get('canon', 0)
        depreciacion = self.request.session.get('depreciacion_periodica', 0)
        impuesto_renta = self.request.session.get('impuesto_renta', 0)
        impuesto_diferido_1 = self.request.session.get('impuesto_diferido', 0)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        valor_razonable = self.request.session.get('valor_razonable', 0)

        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            valor_activo = vlr_razonable_tasa_implicita
            valor_pasivo = vlr_razonable_tasa_implicita
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = valor_pasivo * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                saldo_neto_activo = valor_activo - depreciacion
                saldo_neto_pasivo = valor_pasivo - amortizacion
                impuesto_diferido_activo = saldo_neto_activo * (impuesto_renta / 100)
                impuesto_diferido_pasivo = saldo_neto_pasivo * (impuesto_renta / 100)
                dif_temp_neta = saldo_neto_activo - saldo_neto_pasivo
                dif_imp_dif_neto = impuesto_diferido_activo - impuesto_diferido_pasivo
                amortizacion_data.append({
                    'periodo': periodo,
                    'valor_activo': valor_activo,
                    'valor_pasivo': valor_pasivo,
                    'saldo_neto_activo': saldo_neto_activo,
                    'saldo_neto_pasivo': saldo_neto_pasivo,
                    'impuesto_diferido_activo': (impuesto_diferido_activo*100),
                    'impuesto_diferido_pasivo': (impuesto_diferido_pasivo*100),
                    'amortizacion': amortizacion,
                    'depreciacion': depreciacion,
                    'dif_temp_neta': dif_temp_neta,
                    'dif_imp_dif_neto': (dif_imp_dif_neto *100),
                })
                valor_activo = saldo_neto_activo
                valor_pasivo = saldo_neto_pasivo
            context['activo_uso'] = vlr_razonable_tasa_implicita
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            valor_activo = valor_presente
            valor_pasivo = valor_presente
            amortizacion= 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = valor_pasivo * (tasa_implicita/100)
                amortizacion = canon - interes
                saldo_neto_activo = valor_activo - depreciacion
                saldo_neto_pasivo = valor_pasivo - amortizacion
                impuesto_diferido_activo = saldo_neto_activo * (impuesto_renta / 100)
                impuesto_diferido_pasivo = saldo_neto_pasivo * (impuesto_renta / 100)
                dif_temp_neta = saldo_neto_activo - saldo_neto_pasivo
                dif_imp_dif_neto = impuesto_diferido_activo - impuesto_diferido_pasivo
                amortizacion_data.append({
                    'periodo': periodo,
                    'valor_activo': valor_activo,
                    'valor_pasivo': valor_pasivo,
                    'saldo_neto_activo': saldo_neto_activo,
                    'saldo_neto_pasivo': saldo_neto_pasivo,
                    'impuesto_diferido_activo': (impuesto_diferido_activo*100),
                    'impuesto_diferido_pasivo': (impuesto_diferido_pasivo*100),
                    'amortizacion': amortizacion,
                    'depreciacion': depreciacion,
                    'dif_temp_neta': dif_temp_neta,
                    'dif_imp_dif_neto': (dif_imp_dif_neto *100),
                })
                valor_activo = saldo_neto_activo
                valor_pasivo = saldo_neto_pasivo

            context['activo_uso'] = valor_presente
        context['amortizacion_data'] = amortizacion_data
        context['impuesto_diferido_1'] = impuesto_diferido_1
        return context
    
class Tabla7(TemplateView):
    template_name = 'app/tabla7.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        canon = self.request.session.get('canon', 0)
        depreciacion = self.request.session.get('depreciacion_periodica', 0)
        impuesto_renta = self.request.session.get('impuesto_renta', 0)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        valor_razonable = self.request.session.get('valor_razonable', 0)

        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            saldo_actual = vlr_razonable_tasa_implicita
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                saldo_actual -= amortizacion
                interes = saldo_actual * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                total = interes + depreciacion
                dif_temporal = total - canon
                imp_diferido = dif_temporal * (impuesto_renta / 100)
                amortizacion_data.append({
                    'periodo': periodo,
                    'interes': interes,
                    'depreciacion': depreciacion,
                    'total': total,
                    'canon': canon,
                    'dif_temporal': dif_temporal,
                    'imp_diferido': (imp_diferido*100),
                })
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            saldo_actual = valor_presente
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                saldo_actual -= amortizacion
                interes = saldo_actual * (tasa_implicita/100)
                amortizacion = canon - interes
                total = interes + depreciacion
                dif_temporal = total - canon
                imp_diferido = dif_temporal * (impuesto_renta / 100)
                amortizacion_data.append({
                    'periodo': periodo,
                    'interes': interes,
                    'depreciacion': depreciacion,
                    'total': total,
                    'canon': canon,
                    'dif_temporal': dif_temporal,
                    'imp_diferido': (imp_diferido*100),
                })
        context['amortizacion_data'] = amortizacion_data
        return context

class Tabla8(TemplateView):
    template_name = 'app/tabla8.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        canon = self.request.session.get('canon', 0)
        depreciacion = self.request.session.get('depreciacion_periodica', 0)
        impuesto_renta = self.request.session.get('impuesto_renta', 0)
        impuesto_diferido_1 = self.request.session.get('impuesto_diferido', 0)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        valor_razonable = self.request.session.get('valor_razonable', 0)

        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            #pasivo
            valor_pasivo = vlr_razonable_tasa_implicita
            impuesto_pasivo_anterior = (impuesto_diferido_1/100)
            amortizacion = 0
            #activo
            valor_activo = vlr_razonable_tasa_implicita
            impuesto_activo_anterior = (impuesto_diferido_1/100)

            dif_imp_dif_neto_anterior=0
            amortizacion_data = []
            for periodo in periodos_lista:
                #pasivo
                interes = valor_pasivo * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                saldo_neto_pasivo = valor_pasivo - amortizacion
                impuesto_diferido_pasivo = saldo_neto_pasivo * (impuesto_renta / 100)
                impuesto_pasivo = impuesto_pasivo_anterior - impuesto_diferido_pasivo
                #activo
                saldo_neto_activo = valor_activo - depreciacion
                impuesto_diferido_activo = saldo_neto_activo * (impuesto_renta / 100)
                impuesto_activo = impuesto_activo_anterior -impuesto_diferido_activo

                dif_imp_dif_neto = impuesto_diferido_activo - impuesto_diferido_pasivo
                diferencia_diferencia = dif_imp_dif_neto_anterior - dif_imp_dif_neto
                amortizacion_data.append({
                    #pasivo
                    'periodo': periodo,
                    'impuesto_pasivo': (impuesto_pasivo * 100),
                    #activo
                    'periodo': periodo,
                    'impuesto_activo': (impuesto_activo * 100),

                    'dif_imp_dif_neto': (dif_imp_dif_neto * 100),
                    'diferencia_diferencia': (diferencia_diferencia * 100),

                })
                #pasivo
                valor_pasivo = saldo_neto_pasivo
                impuesto_pasivo_anterior = impuesto_diferido_pasivo
                #activo
                impuesto_activo_anterior = impuesto_diferido_activo
                valor_activo = saldo_neto_activo

                dif_imp_dif_neto_anterior = dif_imp_dif_neto
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            #pasivo
            valor_pasivo = valor_presente
            impuesto_pasivo_anterior = (impuesto_diferido_1/100)
            amortizacion = 0
            #activo
            valor_activo = valor_presente
            impuesto_activo_anterior = (impuesto_diferido_1/100)

            dif_imp_dif_neto_anterior=0
            amortizacion_data = []
            amortizacion_data = []
            for periodo in periodos_lista:
                #pasivo
                interes = valor_pasivo * (tasa_implicita / 100)
                amortizacion = canon - interes
                saldo_neto_pasivo = valor_pasivo - amortizacion
                impuesto_diferido_pasivo = saldo_neto_pasivo * (impuesto_renta / 100)
                impuesto_pasivo = impuesto_pasivo_anterior - impuesto_diferido_pasivo
                #activo
                saldo_neto_activo = valor_activo - depreciacion
                impuesto_diferido_activo = saldo_neto_activo * (impuesto_renta / 100)
                impuesto_activo = impuesto_activo_anterior -impuesto_diferido_activo

                dif_imp_dif_neto = impuesto_diferido_activo - impuesto_diferido_pasivo
                diferencia_diferencia = dif_imp_dif_neto_anterior - dif_imp_dif_neto
                amortizacion_data.append({
                    #pasivo
                    'periodo': periodo,
                    'impuesto_pasivo': (impuesto_pasivo * 100),
                    #activo
                    'periodo': periodo,
                    'impuesto_activo': (impuesto_activo * 100),

                    'dif_imp_dif_neto': (dif_imp_dif_neto * 100),
                    'diferencia_diferencia': (diferencia_diferencia * 100),

                })
                #pasivo
                valor_pasivo = saldo_neto_pasivo
                impuesto_pasivo_anterior = impuesto_diferido_pasivo
                #activo
                impuesto_activo_anterior = impuesto_diferido_activo
                valor_activo = saldo_neto_activo

                dif_imp_dif_neto_anterior = dif_imp_dif_neto
            context['activo_uso'] = valor_presente
        context['amortizacion_data'] = amortizacion_data
        context['impuesto_diferido_1'] = impuesto_diferido_1
        return context
    
class Tabla9(TemplateView):
    template_name = 'app/tabla9.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        depreciacion = self.request.session.get('depreciacion_periodica', 0)
        impuesto_renta = self.request.session.get('impuesto_renta', 0)
        canon = self.request.session.get('canon', 0)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        impuesto_renta = float(impuesto_renta*100)
        impuesto_diferido = self.request.session.get('impuesto_diferido', 0)
        valor_razonable = self.request.session.get('valor_razonable', 0)
        #prueba
        efectivo = canon * periodos
        efectivo_sit_financiera = -efectivo
        impuesto_diferido_sit_financiera = impuesto_diferido - impuesto_diferido
        #estado
        impuesto_diferido_1 = impuesto_diferido
        #pasivo
        impuesto_pasivo_anterior = (impuesto_diferido_1/100)
        amortizacion = 0
        #activo
        impuesto_activo_anterior = (impuesto_diferido_1/100)

        dif_imp_dif_neto_anterior=0
        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            #Balance prueba
            total_activo= efectivo_sit_financiera + vlr_razonable_tasa_implicita + (-vlr_razonable_tasa_implicita)
            pasivo_arrendamiento = vlr_razonable_tasa_implicita - efectivo
            total_pasivo= pasivo_arrendamiento + impuesto_diferido_sit_financiera
            comprobacion_debe = vlr_razonable_tasa_implicita + impuesto_diferido + vlr_razonable_tasa_implicita + impuesto_diferido + efectivo
            comprobacion_haber = efectivo + impuesto_diferido + vlr_razonable_tasa_implicita + efectivo + impuesto_diferido
            comprobacion = total_activo + total_pasivo
            context['activo_uso'] = vlr_razonable_tasa_implicita
            context['amortizacion'] = vlr_razonable_tasa_implicita
            context['amortizacion_sit_financiera'] = -vlr_razonable_tasa_implicita
            context['total_activo'] = total_activo
            context['pasivo_arrendamiento'] = pasivo_arrendamiento
            context['total_pasivo'] = total_pasivo
            context['comprobacion_debe'] = comprobacion_debe
            context['comprobacion_haber'] = comprobacion_haber
            context['comprobacion'] = comprobacion
            #Estado
            utilidad_bruta=0
            context['utilidad_bruta'] = utilidad_bruta

            #pasivo
            valor_pasivo = vlr_razonable_tasa_implicita
            impuesto_pasivo_anterior = (impuesto_diferido_1)
            amortizacion = 0

            #activo
            valor_activo = vlr_razonable_tasa_implicita
            impuesto_activo_anterior = (impuesto_diferido_1)

            dif_imp_dif_neto_anterior=0
            total_impuestos_activos = 0
            total_impuestos_pasivos = 0
            gasto_financiero= 0
            for periodo in periodos_lista:
                #pasivo
                interes = valor_pasivo * (tasa_implicita_porcentaje / 100)
                amortizacion = canon - interes
                saldo_neto_pasivo = valor_pasivo - amortizacion
                impuesto_diferido_pasivo = saldo_neto_pasivo * (impuesto_renta / 100)
                impuesto_pasivo = impuesto_pasivo_anterior - impuesto_diferido_pasivo
                total_impuestos_pasivos  += impuesto_pasivo
                imp_pasivo = impuesto_diferido + total_impuestos_pasivos
                context['imp_pasivo'] = imp_pasivo
                context['total_impuestos_pasivos'] = total_impuestos_pasivos
                #activo
                saldo_neto_activo = valor_activo - depreciacion
                impuesto_diferido_activo = saldo_neto_activo * (impuesto_renta / 100)
                impuesto_activo = impuesto_activo_anterior -impuesto_diferido_activo
                total_impuestos_activos  += impuesto_activo
                imp_activo= impuesto_diferido + total_impuestos_activos
                dif_imp_dif_neto = impuesto_diferido_activo - impuesto_diferido_pasivo
                diferencia_diferencia = dif_imp_dif_neto_anterior - dif_imp_dif_neto
                context['imp_activo'] = imp_activo
                
                gastos_total = imp_activo - imp_pasivo
                activo_uso = vlr_razonable_tasa_implicita
                utilidad_operacion = utilidad_bruta + gastos_total - activo_uso

                gasto_financiero += interes
                utilidad_antes_impuestos = utilidad_operacion - gasto_financiero
                impuestos=0
                suma_debe = imp_activo + activo_uso + gasto_financiero
                suma_haber = imp_pasivo
                utilidad_neta = utilidad_antes_impuestos - impuestos
                perdida_total = utilidad_neta
                if suma_debe > suma_haber:
                    perdida_debe = suma_debe - suma_haber
                    context['perdida_debe'] = perdida_debe
                else:
                    perdida_haber =  suma_haber - suma_debe
                    context['perdida_haber'] = perdida_haber

                context['gastos_total'] = gastos_total
                context['utilidad_operacion'] = utilidad_operacion
                context['gasto_financiero'] = gasto_financiero
                context['utilidad_antes_impuestos'] = utilidad_antes_impuestos
                context['impuestos'] = impuestos
                context['utilidad_neta'] = utilidad_neta
                context['suma_debe'] = suma_debe
                context['suma_haber'] = suma_haber
                context['perdida_total'] = perdida_total


                #pasivo
                valor_pasivo = saldo_neto_pasivo
                impuesto_pasivo_anterior = impuesto_diferido_pasivo
                #activo
                impuesto_activo_anterior = impuesto_diferido_activo
                valor_activo = saldo_neto_activo

        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            #Balance prueba
            total_activo= efectivo_sit_financiera + valor_presente + (-valor_presente)
            pasivo_arrendamiento = valor_presente - efectivo
            total_pasivo= pasivo_arrendamiento + impuesto_diferido_sit_financiera
            comprobacion_debe = valor_presente + impuesto_diferido + valor_presente + impuesto_diferido + efectivo
            comprobacion_haber = efectivo + impuesto_diferido + valor_presente + efectivo + impuesto_diferido
            comprobacion = total_activo + total_pasivo
            context['activo_uso'] = valor_presente
            context['amortizacion'] = valor_presente
            context['amortizacion_sit_financiera'] = -valor_presente
            context['total_activo'] = total_activo
            context['pasivo_arrendamiento'] = pasivo_arrendamiento
            context['total_pasivo'] = total_pasivo
            context['comprobacion_debe'] = comprobacion_debe
            context['comprobacion_haber'] = comprobacion_haber
            context['comprobacion'] = comprobacion
            #Estado
            utilidad_bruta=0
            context['utilidad_bruta'] = utilidad_bruta

            #pasivo
            valor_pasivo = valor_presente
            impuesto_pasivo_anterior = (impuesto_diferido_1)
            amortizacion = 0

            #activo
            valor_activo = valor_presente
            impuesto_activo_anterior = (impuesto_diferido_1)

            dif_imp_dif_neto_anterior=0
            total_impuestos_activos = 0
            total_impuestos_pasivos = 0
            gasto_financiero= 0
            for periodo in periodos_lista:
                #pasivo
                interes = valor_pasivo * (tasa_implicita / 100)
                amortizacion = canon - interes
                saldo_neto_pasivo = valor_pasivo - amortizacion
                impuesto_diferido_pasivo = saldo_neto_pasivo * (impuesto_renta / 100)
                impuesto_pasivo = impuesto_pasivo_anterior - impuesto_diferido_pasivo
                total_impuestos_pasivos  += impuesto_pasivo
                imp_pasivo = impuesto_diferido + total_impuestos_pasivos
                context['imp_pasivo'] = imp_pasivo
                context['total_impuestos_pasivos'] = total_impuestos_pasivos
                #activo
                saldo_neto_activo = valor_activo - depreciacion
                impuesto_diferido_activo = saldo_neto_activo * (impuesto_renta / 100)
                impuesto_activo = impuesto_activo_anterior -impuesto_diferido_activo
                total_impuestos_activos  += impuesto_activo
                imp_activo= impuesto_diferido + total_impuestos_activos
                dif_imp_dif_neto = impuesto_diferido_activo - impuesto_diferido_pasivo
                diferencia_diferencia = dif_imp_dif_neto_anterior - dif_imp_dif_neto
                context['imp_activo'] = imp_activo
                
                gastos_total = imp_activo - imp_pasivo
                activo_uso = valor_presente
                utilidad_operacion = utilidad_bruta + gastos_total - activo_uso

                gasto_financiero += interes
                utilidad_antes_impuestos = utilidad_operacion - gasto_financiero
                impuestos=0
                suma_debe = imp_activo + activo_uso + gasto_financiero
                suma_haber = imp_pasivo
                utilidad_neta = utilidad_antes_impuestos - impuestos
                perdida_total = utilidad_neta
                if suma_debe > suma_haber:
                    perdida_debe = suma_debe - suma_haber
                    context['perdida_debe'] = perdida_debe
                else:
                    perdida_haber =  suma_haber - suma_debe
                    context['perdida_haber'] = perdida_haber

                context['gastos_total'] = gastos_total
                context['utilidad_operacion'] = utilidad_operacion
                context['gasto_financiero'] = gasto_financiero
                context['utilidad_antes_impuestos'] = utilidad_antes_impuestos
                context['impuestos'] = impuestos
                context['utilidad_neta'] = utilidad_neta
                context['suma_debe'] = suma_debe
                context['suma_haber'] = suma_haber
                context['perdida_total'] = perdida_total


                #pasivo
                valor_pasivo = saldo_neto_pasivo
                impuesto_pasivo_anterior = impuesto_diferido_pasivo
                #activo
                impuesto_activo_anterior = impuesto_diferido_activo
                valor_activo = saldo_neto_activo

        context['impuesto_renta'] = impuesto_renta
        context['efectivo'] = efectivo
        context['efectivo_sit_financiera'] = efectivo_sit_financiera
        context['impuesto_diferido'] = impuesto_diferido
        context['impuesto_diferido_sit_financiera'] = impuesto_diferido_sit_financiera
        return context
    
class Tabla10 (TemplateView):
    template_name = 'app/tabla10.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodos = self.request.session.get('tiempo_arrendamiento', 0)
        periodos_lista = list(range(1, periodos + 1))
        canon = self.request.session.get('canon', 0)
        depreciacion = self.request.session.get('depreciacion_periodica', 0)
        impuesto_renta = self.request.session.get('impuesto_renta', 0)
        impuesto_renta = float(impuesto_renta*100)
        valor_razonable = self.request.session.get('valor_razonable', 0)
        if valor_razonable == 'si':
            tasa_implicita_porcentaje = self.request.session.get('tasa_implicita_porcentaje', 0)
            vlr_razonable_tasa_implicita = self.request.session.get('vlr_razonable_tasa_implicita', 0)
            vlr_razonable_tasa_implicita = int(vlr_razonable_tasa_implicita)
            saldo_actual = vlr_razonable_tasa_implicita
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita_porcentaje/100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                total = interes + depreciacion
                diferencia = total - canon
                impuesto_diferencia = diferencia * (impuesto_renta/100)
                amortizacion_data.append({
                    'periodo': periodo,
                    'canon': canon,
                    'interes': interes,
                    'depreciacion': depreciacion,
                    'total': total,
                    'diferencia': diferencia,
                    'impuesto_diferencia': impuesto_diferencia,
                })
            context['activo_uso'] = vlr_razonable_tasa_implicita
        else:
            tasa_implicita = self.request.session.get('tasa_implicita', 0)
            valor_presente = self.request.session.get('valor_presente', 0)
            valor_presente = int(valor_presente)
            saldo_actual = valor_presente
            amortizacion = 0
            amortizacion_data = []
            for periodo in periodos_lista:
                interes = saldo_actual * (tasa_implicita/100)
                amortizacion = canon - interes
                saldo_actual -= amortizacion
                total = interes + depreciacion
                diferencia = total - canon
                impuesto_diferencia = diferencia * (impuesto_renta/100)
                amortizacion_data.append({
                    'periodo': periodo,
                    'canon': canon,
                    'interes': interes,
                    'depreciacion': depreciacion,
                    'total': total,
                    'diferencia': diferencia,
                    'impuesto_diferencia': impuesto_diferencia,
                })
            context['activo_uso'] = valor_presente
        context['amortizacion_data'] = amortizacion_data
        context['canon'] = canon
        return context 
    
class Tabla11 (TemplateView):
    template_name = 'app/tabla11.html'

class Tabla12 (TemplateView):
    template_name = 'app/tabla12.html'