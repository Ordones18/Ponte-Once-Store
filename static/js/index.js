document.addEventListener('DOMContentLoaded', () => {
    console.log("Index View Loaded");

    // Simple parallax effect for hero
    const hero = document.querySelector('.hero');
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        hero.style.backgroundPositionY = -(scrolled * 0.5) + 'px';
    });
});
