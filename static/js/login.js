$(document).ready(function() {
    $('#loginForm').on('submit', function(event) {
        event.preventDefault(); // Evita el envío normal del formulario

        const correo = $('#correo').val();
        const password = $('#password').val();

        $.ajax({
            type: 'POST',
            url: '/login',  // Asegúrate de que esta URL sea correcta
            data: JSON.stringify({ correo: correo, password: password }),
            contentType: 'application/json',
            success: function(response) {
                if (response.success) {
                    // Redirige a la página de verificación de código
                    window.location.href = '/verificar_codigo';
                } else {
                    $('#flash-message').text(response.message).show(); // Muestra mensaje de error
                }
            },
            error: function() {
                $('#flash-message').text("Error en el servidor. Inténtalo de nuevo.").show();
            }
        });
    });
});
