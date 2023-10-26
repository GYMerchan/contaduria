$(document).ready(function() {
    $("input[type='reset']").click(function() {
        var csrftoken = $("[name=csrfmiddlewaretoken]").val();
        $.ajax({
            type: "POST",
            url: "/aplicativo/borrar/",
            data: {},
            headers: { "X-CSRFToken": csrftoken },
            success: function(response) {
                alert("Datos borrados correctamente");
                toastr.success("Formato no soportado. Solo se permiten .docx y .xlsx");
            },
            error: function(xhr, textStatus, errorThrown) {
                console.error("Error en la solicitud:", textStatus);
                console.error("Error arrojado:", errorThrown);
            }
        });
    });
});
