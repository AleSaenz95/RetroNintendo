document.addEventListener("DOMContentLoaded", () => {
    const slides = document.querySelectorAll(".onboarding-slide");
    console.log("Diapositivas encontradas:", slides.length); // Verifica el número de diapositivas encontradas

    if (!slides || slides.length === 0) {
        console.error("No se encontraron diapositivas con la clase '.onboarding-slide'.");
        return;
    }

    let currentSlide = 0;

    // Mostrar la primera diapositiva al cargar
    slides[currentSlide].classList.add("active");

    // Botones "Siguiente"
    document.querySelectorAll(".next-slide").forEach((button) => {
        button.addEventListener("click", () => {
            slides[currentSlide].classList.remove("active");
            currentSlide++;
            if (currentSlide < slides.length) {
                slides[currentSlide].classList.add("active");
            }
        });
    });

    // Botón "Cerrar"
    const closeButton = document.getElementById("close-onboarding");
    if (closeButton) {
        closeButton.addEventListener("click", () => {
            document.cookie = "onboardingSeen=true; path=/";
            window.location.href = "/";
        });
    }
});
