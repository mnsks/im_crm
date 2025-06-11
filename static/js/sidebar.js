document.addEventListener('DOMContentLoaded', function() {
    // Marquer le lien actif
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            
            // Trouver la section parente et ajouter une classe active
            const parentSection = link.closest('.nav-section');
            if (parentSection) {
                parentSection.classList.add('active-section');
            }
        }
    });

    // Gestion du responsive
    const sidebar = document.getElementById('mainSidebar');
    const toggleButton = document.querySelector('.topbar-toggler');
    const content = document.querySelector('.content');

    if (toggleButton && sidebar) {
        toggleButton.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }

    if (content && sidebar) {
        content.addEventListener('click', function() {
            if (window.innerWidth <= 768 && sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
            }
        });
    }

    // Effet de survol amélioré
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.transform = 'scale(1.1)';
                icon.style.transition = 'transform 0.2s ease';
            }
        });

        link.addEventListener('mouseleave', function() {
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.transform = 'scale(1)';
            }
        });
    });

    // Gestion des badges de notification
    function updateBadges() {
        const badges = document.querySelectorAll('.nav-badge');
        badges.forEach(badge => {
            if (parseInt(badge.textContent) === 0) {
                badge.style.display = 'none';
            } else {
                badge.style.display = 'block';
            }
        });
    }

    // Appeler updateBadges au chargement
    updateBadges();

    // Écouter les changements de taille d'écran
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('show');
        }
    });
});
