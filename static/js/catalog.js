document.addEventListener('DOMContentLoaded', () => {
    console.log("Catalog View Loaded");

    // Future filter logic could go here
    const cards = document.querySelectorAll('.product-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.animation = `fadeInUp 0.5s ease-out ${index * 0.1}s forwards`;
    });
});
