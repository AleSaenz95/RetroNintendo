document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM cargado correctamente");

    const onboardingSeen = localStorage.getItem("onboardingSeen");
    console.log("Valor de onboardingSeen:", onboardingSeen);

    const slides = document.querySelectorAll(".onboarding-slide");
    console.log("Diapositivas encontradas:", slides.length);

    let currentSlide = 0;

    if (!onboardingSeen) {
        console.log("Mostrando onboarding...");
        document.getElementById("onboarding-container").style.display = "flex";
        slides[currentSlide].classList.add("active");

        document.querySelectorAll(".next-slide").forEach((button) =>
            button.addEventListener("click", () => {
                console.log("Siguiente diapositiva");
                slides[currentSlide].classList.remove("active");
                currentSlide++;
                if (currentSlide < slides.length) {
                    slides[currentSlide].classList.add("active");
                }
            })
        );

        document.getElementById("close-onboarding").addEventListener("click", () => {
            console.log("Onboarding completado");
            localStorage.setItem("onboardingSeen", "true");
            document.getElementById("onboarding-container").style.display = "none";
        });
    }
});
