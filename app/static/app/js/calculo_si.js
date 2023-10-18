$(document).ready(function() {
    function calcularTIR() {
        var csrfToken = $("input[name='csrfmiddlewaretoken']").val();
        var canon = ($("#canon_si").val());
        var tiempoArrendamiento = ($("#tiempo_arrendamiento_si").val());
        var valorRazonable = ($("#vlr_razonable_tasa_implicita_si").val());
        if ((canon) && (tiempoArrendamiento) && (valorRazonable)) {
            
            var data = {
                csrfmiddlewaretoken: csrfToken,
                canon: canon,
                tiempoArrendamiento: tiempoArrendamiento,
                valorRazonable: valorRazonable
            };
            $.ajax({
                type: "POST",
                url: "/aplicativo/tir/",
                data: data,
                success: function(response) {
                    console.log("Respuesta del servidor:", response);
                    $("#tasa_implicita_porcentaje_si").val((response.tir));
                    $("#depreciacion_periodica_si").val(response.depreciacion);
                },
                error: function(xhr, textStatus, errorThrown) {
                    console.error("Error en la solicitud:");
                    console.error("Estado de la solicitud:", textStatus);
                    console.error("Error arrojado:", errorThrown);
                }
            });
        } else {

        }
    }

    $("#canon_si, #tiempo_arrendamiento_si, #vlr_razonable_tasa_implicita_si").on("input", calcularTIR);
});

