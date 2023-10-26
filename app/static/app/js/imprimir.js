document.getElementById('imprimirTabla').addEventListener('click', function () {
    // Oculta todo antes de imprimir
    document.body.classList.add('printing');

    // Imprime la página
    window.print();

    // Restaura la visualización normal
    document.body.classList.remove('printing');
});