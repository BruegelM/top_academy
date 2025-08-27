document.addEventListener('DOMContentLoaded', () => {
    // Основные элементы галереи
    const gallery = document.querySelector('.gallery-container');
    const items = Array.from(document.querySelectorAll('.gallery-item'));
    const dots = Array.from(document.querySelectorAll('.dotnav-item'));
    const prevBtn = document.querySelector('.prev');
    const nextBtn = document.querySelector('.next');
    const header = document.querySelector('.apple-header');
    const hero = document.querySelector('.hero');
    
    // Состояние галереи
    let currentIndex = 0;
    let itemWidth = items[0]?.offsetWidth || 0;
    let lastScroll = 0;
    let autoScroll;

    // Функции галереи
    const updateGallery = () => {
        if (!gallery || !items.length) return;
        
        gallery.style.transform = `translateX(-${currentIndex * itemWidth}px)`;
        dots.forEach((dot, index) => {
            dot.classList.toggle('current', index === currentIndex);
        });
    };

    const startAutoScroll = () => {
        clearInterval(autoScroll);
        autoScroll = setInterval(() => {
            currentIndex = (currentIndex < items.length - 1) ? currentIndex + 1 : 0;
            updateGallery();
        }, 5000);
    };

    // Обработчики событий галереи
    const setupGallery = () => {
        if (!items.length) return;

        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                currentIndex = index;
                updateGallery();
            });
        });

        prevBtn?.addEventListener('click', () => {
            currentIndex = (currentIndex > 0) ? currentIndex - 1 : items.length - 1;
            updateGallery();
        });

        nextBtn?.addEventListener('click', () => {
            currentIndex = (currentIndex < items.length - 1) ? currentIndex + 1 : 0;
            updateGallery();
        });

        gallery?.addEventListener('mouseenter', () => clearInterval(autoScroll));
        gallery?.addEventListener('mouseleave', startAutoScroll);
        
        startAutoScroll();
    };

    // Параллакс и скролл-эффекты
    const setupScrollEffects = () => {
        window.addEventListener('scroll', () => {
            const currentScroll = window.scrollY;
            
            // Обработка хедера
            if (header) {
                if (currentScroll <= 0) {
                    header.style.transform = 'translateY(0)';
                } else if (currentScroll > lastScroll && currentScroll > 100) {
                    header.style.transform = 'translateY(-100%)';
                } else {
                    header.style.transform = 'translateY(0)';
                }
            }
            
            // Параллакс для hero-секции
            if (hero) {
                hero.style.backgroundPositionY = `-${currentScroll * 0.5}px`;
            }
            
            lastScroll = currentScroll;
        });
    };

    // Анимации появления
    const setupAnimations = () => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });

        // Анимация product cards
        document.querySelectorAll('.product-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.5s ease-out';
            observer.observe(card);
        });

        // Анимация feature cards
        document.querySelectorAll('.gallery-item').forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = `opacity 0.5s ease-out ${index * 0.1}s, transform 0.5s ease-out ${index * 0.1}s`;
            observer.observe(card);
        });
    };

    // Модальные окна
    const setupModals = () => {
        document.querySelectorAll('.card-cta-modal-button').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const card = button.closest('.gallery-item');
                if (card) {
                    const cardId = card.getAttribute('data-analytics-gallery-item-id') || 'unknown';
                    openModal(cardId);
                }
            });
        });
    };

    // Ресайз
    const handleResize = () => {
        if (items.length) {
            itemWidth = items[0].offsetWidth;
            updateGallery();
        }
    };

    // Инициализация
    const init = () => {
        setupGallery();
        setupScrollEffects();
        setupAnimations();
        setupModals();
        window.addEventListener('resize', handleResize);
    };

    init();
});

// Модальное окно (можно вынести в отдельный файл)
function openModal(contentId) {
    console.log(`Открыто модальное окно с контентом: ${contentId}`);
    // В реальном проекте использовать специализированное решение для модальных окон
    alert(`Открыта информация о: ${contentId.replace(/-/g, ' ')}`);
}
