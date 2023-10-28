$(document).ready(function() {
    $("#tasa_incremental_no").on("input", function() {
        var tasa_incremental = $(this).val(); 
        $("#tasa_implicita_no").val(tasa_incremental+ "%");
    });

    function quitarPuntosDeNumero(numero) {
        // Eliminar los puntos de mil y de millón
        return numero.replace(/\./g, "");
    }


    function formatearNumeroConPuntos(numero) {
        // Formatear el número con puntos de mil y de millón
        return numero.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    function CalcularValorRazonable() {
        var csrfToken = $("input[name='csrfmiddlewaretoken']").val();
        var canon = ($("#canon_no").val().replace(/[^0-9.]/g, ""));
        var tiempoArrendamiento = ($("#tiempo_arrendamiento_no").val().replace(/[^0-9.]/g, ""));
        var tasaImplicta = ($("#tasa_incremental_no").val().replace("%", ""));
        if ((canon) && (tiempoArrendamiento) && (tasaImplicta)) {
                
            var data = {
                csrfmiddlewaretoken: csrfToken,
                canon: canon,
                tiempoArrendamiento: tiempoArrendamiento,
                tasaImplicta: tasaImplicta
            };
            $.ajax({
                type: "POST",
                url: "/aplicativo/vp/",
                data: data,
                success: function(response) {
                    console.log("Respuesta del servidor:", response);
                    $("#valor_presente_no").val(formatearNumeroConPuntos(response.valor_razonable));
                    $("#depreciacion_periodica_no").val(formatearNumeroConPuntos(response.depreciacion));

                    amortizacion_activo
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
    $("#canon_no, #tiempo_arrendamiento_no, #tasa_incremental_no").on("input", CalcularValorRazonable);

    // Obtén referencias a los elementos de entrada
	const tasaIncrementalInput = document.getElementById("tasa_incremental_no");
	const tasaImplicitaInput = document.getElementById("tasa_implicita_no");

	// Escucha el evento "input" en ambos campos de entrada
	tasaIncrementalInput.addEventListener("input", function() {
		actualizarValorConPorcentaje(tasaIncrementalInput, tasaImplicitaInput);
	});

	tasaImplicitaInput.addEventListener("input", function() {
		actualizarValorConPorcentaje(tasaImplicitaInput, tasaIncrementalInput);
	});

	// Función para actualizar el valor con el símbolo de porcentaje
	function actualizarValorConPorcentaje(inputOrigen, inputDestino) {
		const valor = inputOrigen.value.trim();
		
		// Verifica si el valor es un número
		if (/^\d+(\.\d+)?%?$/.test(valor)) {
		// Si no termina en "%", agrega el símbolo de porcentaje
		if (!valor.endsWith("%")) {
			inputOrigen.value = valor + "%";
		}
		// Actualiza el valor en el otro campo
		inputDestino.value = valor + "%";
		} else {
		// Si el valor no es válido, muestra un mensaje de error o un valor predeterminado
		inputDestino.value = "Valor no válido";
		}
	}

    // Escuchar el evento "input" en los campos relevantes y formatear los números
    $("#valor_presente_no, #depreciacion_periodica_no, #canon_no").on("input", function() {
        var valor = $(this).val().replace(/[^0-9.]/g, ""); // Quitar caracteres no numéricos
        $(this).val(formatearNumeroConPuntos(valor));
    });
    // Agregar un evento al formulario para quitar los puntos antes del envío
    $("form").on("submit", function() {
        $("#canon_no").val(quitarPuntosDeNumero($("#canon_no").val().replace(/[^0-9.]/g, "")));
        $("#valor_presente_no").val(quitarPuntosDeNumero($("#valor_presente_no").val().replace(/[^0-9.]/g, "")));
        $("#depreciacion_periodica_no").val(quitarPuntosDeNumero($("#depreciacion_periodica_no").val().replace(/[^0-9.]/g, "")));
        $("#tasa_implicita_no").val($("#tasa_implicita_no").val().replace("%", ""));
        $("#tasa_incremental_no").val($("#tasa_incremental_no").val().replace("%", ""));
    });
});

 