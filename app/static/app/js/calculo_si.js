$(document).ready(function() {
    // Función para quitar los puntos de los números
    function quitarPuntosDeNumero(numero) {
        return numero.replace(/\./g, "");
    }

    // Función para formatear números con puntos de miles y millones
    function formatearNumeroConPuntos(numero) {
        return numero.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    // Función para calcular la TIR
    function calcularTIR() {
        var csrfToken = $("input[name='csrfmiddlewaretoken']").val();
        var canon = ($("#canon_si").val().replace(/[^0-9.]/g, ""));
        var tiempoArrendamiento = ($("#tiempo_arrendamiento_si").val());
        var valorRazonable = ($("#vlr_razonable_tasa_implicita_si").val().replace(/[^0-9.]/g, ""));
        if (canon && tiempoArrendamiento && valorRazonable) {
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
                    $("#depreciacion_periodica_si").val(formatearNumeroConPuntos(response.depreciacion));
                },
                error: function(xhr, textStatus, errorThrown) {
                    console.error("Error en la solicitud:");
                    console.error("Estado de la solicitud:", textStatus);
                    console.error("Error arrojado:", errorThrown);
                }
            });
        }
    }
    $("#canon_si, #tiempo_arrendamiento_si, #vlr_razonable_tasa_implicita_si").on("input", calcularTIR);
    /* function actualizarValorConPorcentaje(inputOrigen, inputDestino) {
        if (inputOrigen) {
            const valor = parseFloat(inputOrigen.value); // Convierte el valor a número
            if (!isNaN(valor)) {
                inputOrigen.value = valor + "%"; // Agrega el símbolo de porcentaje
                inputDestino.value = valor + "%";
            } else {
                inputDestino.value = "Valor no válido";
            }
        }
    } */
    // Escuchar el evento "input" en los campos relevantes y formatear los números
    $("#vlr_razonable_tasa_implicita_si, #canon_si, #depreciacion_periodica_si").on("input", function() {
        var valor = $(this).val().replace(/[^0-9.]/g, "");
        $(this).val(formatearNumeroConPuntos(valor));
    });

    // Agregar un evento al formulario para quitar los puntos antes del envío
    $("form").on("submit", function() {
        $("#canon_si").val(quitarPuntosDeNumero($("#canon_si").val().replace(/[^0-9.]/g, "")));
        $("#vlr_razonable_tasa_implicita_si").val(quitarPuntosDeNumero($("#vlr_razonable_tasa_implicita_si").val().replace(/[^0-9.]/g, "")));
        $("#depreciacion_periodica_si").val(quitarPuntosDeNumero($("#depreciacion_periodica_si").val().replace(/[^0-9.]/g, "")));
    });
});
