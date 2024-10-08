document.addEventListener("DOMContentLoaded", function() {
    const particlesContainer = document.createElement("div");
    particlesContainer.className = "particles";
    document.querySelector(".interactive-bg").appendChild(particlesContainer);

    for (let i = 0; i < 100; i++) {
        const particle = document.createElement("div");
        particle.className = "particle";
        particlesContainer.appendChild(particle);
    }
});
