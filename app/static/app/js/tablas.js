document.addEventListener("DOMContentLoaded", function() {
    var numberElements = document.querySelectorAll(".format-number");
    numberElements.forEach(function(element) {
      var number = parseFloat(element.textContent);
      if (!isNaN(number)) {
        var formattedNumber = numberWithCommas(number);
        element.textContent = formattedNumber;
      }
    });
  
    function numberWithCommas(x) {
      return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
  });