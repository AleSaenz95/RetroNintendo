document.addEventListener("DOMContentLoaded", () => {
    const slides = document.querySelectorAll(".onboarding-slide");
    let currentSlide = 0;

    // Mostrar la primera diapositiva al cargar
    slides[currentSlide].classList.add("active");

    // Función para cambiar a la siguiente diapositiva
    const showNextSlide = () => {
        slides[currentSlide].classList.remove("active"); // Oculta la actual
        currentSlide++;

        if (currentSlide < slides.length - 1) {
            // Muestra la siguiente diapositiva mientras no sea la última
            slides[currentSlide].classList.add("active");
        } else if (currentSlide === slides.length - 1) {
            // Muestra la última diapositiva y detiene el intervalo
            slides[currentSlide].classList.add("active");
            clearInterval(slideInterval); // Detén el intervalo al llegar a la última
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
