$(document).ready(function() {
    $("#tasa_incremental_no").on("input", function() {
        var tasa_incremental = $(this).val(); 
        $("#tasa_implicita_no").val(tasa_incremental);
    });

    function CalcularValorRazonable() {
        var csrfToken = $("input[name='csrfmiddlewaretoken']").val();
        var canon = ($("#canon_no").val());
        var tiempoArrendamiento = ($("#tiempo_arrendamiento_no").val());
        var tasaImplicta = ($("#tasa_implicita_no").val());
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
                    $("#valor_presente_no").val(response.valor_razonable);
                    $("#depreciacion_periodica_no").val(response.depreciacion);

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
    $("#canon_no, #tiempo_arrendamiento_no, #tasa_implicita_no").on("input", CalcularValorRazonable);
});

 