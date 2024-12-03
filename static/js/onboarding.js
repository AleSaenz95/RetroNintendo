document.addEventListener("DOMContentLoaded", () => {
    const slides = document.querySelectorAll(".onboarding-slide");
    let currentSlide = 0;

    // Mostrar la primera diapositiva al cargar
    slides[currentSlide].classList.add("active");

    // Función para cambiar a la siguiente diapositiva
    const showNextSlide = () => {
        slides[currentSlide].classList.remove("active"); // Oculta la actual
        currentSlide++;

        if (currentSlide < slides.length) {
            slides[currentSlide].classList.add("active"); // Muestra la siguiente
        } else {
            clearInterval(slideInterval); // Detén el intervalo cuando termine
        }
    };

    // Cambiar diapositiva automáticamente cada 3 segundos
    const slideInterval = setInterval(showNextSlide, 3000);

    // Botón "Empezar" en la última diapositiva
    const closeButton = document.getElementById("close-onboarding");
    if (closeButton) {
        closeButton.addEventListener("click", () => {
            document.cookie = "onboardingSeen=true; path=/"; // Guardar cookie
            window.location.href = "/"; // Redirigir al index
        });
    }
});
