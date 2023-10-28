$(document).ready(function() {
    $("input[type='reset']").click(function() {
        var csrftoken = $("[name=csrfmiddlewaretoken]").val();
        $.ajax({
            type: "POST",
            url: "/aplicativo/borrar/",
            data: {},
            headers: { "X-CSRFToken": csrftoken },
            success: function(response) {
                Swal.fire({
                    icon: 'success',
                    title: 'Datos borrados',
                    text: 'Vuelve a diligenciar los datos',
                });
            },
            error: function(xhr, textStatus, errorThrown) {
                console.error("Error en la solicitud:", textStatus);
                console.error("Error arrojado:", errorThrown);
            }
        });
    });
});
