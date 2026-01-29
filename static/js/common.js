console.log("AORUS Store Initialized");

// Global effects or analytics could go here
document.addEventListener('DOMContentLoaded', () => {
    // Add subtle hover effect to logo
    const logo = document.querySelector('.logo');
    if (logo) {
        logo.addEventListener('mouseover', () => {
            // Updated style logic removed to rely on CSS
        });
        logo.addEventListener('mouseout', () => {
            // Updated style logic removed to rely on CSS
        });
    }

    // Hamburger Menu Logic
    const hamburger = document.querySelector(".hamburger");
    const navMenu = document.querySelector(".nav-links");

    if (hamburger && navMenu) {
        hamburger.addEventListener("click", () => {
            hamburger.classList.toggle("active");
            navMenu.classList.toggle("active");
        });

        // Close menu when clicking a link
        document.querySelectorAll(".nav-links li a").forEach(n => n.addEventListener("click", () => {
            hamburger.classList.remove("active");
            navMenu.classList.remove("active");
        }));
    }
});
