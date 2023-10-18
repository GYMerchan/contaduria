document.addEventListener("DOMContentLoaded", function () {
  // Define una función para manejar el comportamiento de mostrar/ocultar
  function toggleLista(boton, listaDesplegable) {
      if (listaDesplegable.style.display === "none" || listaDesplegable.style.display === "") {
          listaDesplegable.style.display = "block";
      } else {
          listaDesplegable.style.display = "none";
      }
  }

  // Utiliza un bucle para repetir el proceso para cada conjunto de botón y lista
  for (let i = 0; i <= 7; i++) {
      const botonMostrarLista = document.getElementById(`mostrarLista${i}`);
      const listaDesplegable = document.getElementById(`listaDesplegable${i}`);

      // Oculta la lista al cargar la página
      listaDesplegable.style.display = "none";

      // Agrega el evento de escucha al botón
      botonMostrarLista.addEventListener("click", function () {
          toggleLista(botonMostrarLista, listaDesplegable);
      });
  }
});
