/**
 * ===== FASE 4: UX PREMIUM =====
 * Sistema de micro-interacciones y componentes premium
 */

class PremiumUX {
    constructor() {
        this.isInitialized = false;
        this.currentTheme = 'light';
        this.animationsEnabled = true;
        this.toastContainer = null;
        this.modalBackdrop = null;
        this.activeModals = new Set();
        this.intersectionObservers = new Map();
        this.debounceTimers = new Map();
        
        // Configuración de accesibilidad
        this.accessibilityConfig = {
            reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
            highContrast: window.matchMedia('(prefers-contrast: high)').matches,
            largeText: window.matchMedia('(prefers-reduced-motion: reduce)').matches
        };
    }

    /**
     * Inicializar el sistema UX Premium
     */
    init() {
        if (this.isInitialized) return;
        
        console.log('🎨 Inicializando UX Premium...');
        
        this.setupTheme();
        this.setupAccessibility();
        this.setupAnimations();
        this.setupMicroInteractions();
        this.setupNotifications();
        this.setupModals();
        this.setupTooltips();
        this.setupLoadingStates();
        this.setupFormEnhancements();
        this.setupKeyboardNavigation();
        this.setupIntersectionObserver();
        this.setupPerformanceOptimizations();
        
        this.isInitialized = true;
        console.log('✅ UX Premium inicializado correctamente');
        
        // Emitir evento de inicialización
        this.emit('premium-ux:initialized');
    }

    /**
     * Configurar sistema de temas
     */
    setupTheme() {
        const savedTheme = localStorage.getItem('premium-ux-theme') || 'light';
        this.setTheme(savedTheme);
        
        // Botón de cambio de tema
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-theme-toggle]')) {
                e.preventDefault();
                this.toggleTheme();
            }
        });
        
        // Detectar preferencias del sistema
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('premium-ux-theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    /**
     * Cambiar tema
     */
    setTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('premium-ux-theme', theme);
        
        // Actualizar meta theme-color
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#1a202c' : '#ffffff');
        }
        
        this.emit('premium-ux:theme-changed', { theme });
    }

    /**
     * Alternar tema
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    /**
     * Configurar accesibilidad
     */
    setupAccessibility() {
        // Respetar preferencias de movimiento reducido
        if (this.accessibilityConfig.reducedMotion) {
            this.animationsEnabled = false;
            document.documentElement.classList.add('reduced-motion');
        }
        
        // Configurar navegación por teclado
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });
        
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
        
        // Mejorar contraste si es necesario
        if (this.accessibilityConfig.highContrast) {
            document.documentElement.classList.add('high-contrast');
        }
        
        // Configurar skip links
        this.setupSkipLinks();
    }

    /**
     * Configurar skip links para accesibilidad
     */
    setupSkipLinks() {
        const skipLinks = document.querySelectorAll('.skip-link');
        skipLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.focus();
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    /**
     * Configurar animaciones
     */
    setupAnimations() {
        if (!this.animationsEnabled) return;
        
        // Animaciones de entrada
        const animateOnScroll = (entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        };
        
        const scrollObserver = new IntersectionObserver(animateOnScroll, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        document.querySelectorAll('[data-animate]').forEach(el => {
            scrollObserver.observe(el);
        });
        
        // Animaciones de hover
        this.setupHoverAnimations();
    }

    /**
     * Configurar animaciones de hover
     */
    setupHoverAnimations() {
        document.querySelectorAll('[data-hover-animate]').forEach(el => {
            el.addEventListener('mouseenter', () => {
                if (this.animationsEnabled) {
                    el.classList.add('hover-animate');
                }
            });
            
            el.addEventListener('mouseleave', () => {
                el.classList.remove('hover-animate');
            });
        });
    }

    /**
     * Configurar micro-interacciones
     */
    setupMicroInteractions() {
        // Efectos de ripple en botones
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn')) {
                this.createRippleEffect(e);
            }
        });
        
        // Efectos de focus mejorados
        document.addEventListener('focusin', (e) => {
            if (e.target.matches('.form-control, .btn')) {
                e.target.classList.add('focus-enhanced');
            }
        });
        
        document.addEventListener('focusout', (e) => {
            if (e.target.matches('.form-control, .btn')) {
                e.target.classList.remove('focus-enhanced');
            }
        });
        
        // Efectos de carga
        this.setupLoadingEffects();
    }

    /**
     * Crear efecto ripple
     */
    createRippleEffect(event) {
        const button = event.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    /**
     * Configurar efectos de carga
     */
    setupLoadingEffects() {
        document.querySelectorAll('[data-loading]').forEach(el => {
            el.addEventListener('click', () => {
                this.showLoadingState(el);
            });
        });
    }

    /**
     * Mostrar estado de carga
     */
    showLoadingState(element) {
        const originalContent = element.innerHTML;
        const loadingSpinner = '<span class="loading"></span>';
        
        element.innerHTML = loadingSpinner;
        element.disabled = true;
        element.classList.add('loading');
        
        // Simular carga (en producción, esto sería una promesa real)
        setTimeout(() => {
            element.innerHTML = originalContent;
            element.disabled = false;
            element.classList.remove('loading');
        }, 2000);
    }

    /**
     * Configurar sistema de notificaciones
     */
    setupNotifications() {
        // Crear contenedor de notificaciones
        this.toastContainer = document.createElement('div');
        this.toastContainer.className = 'toast-container';
        document.body.appendChild(this.toastContainer);
        
        // Escuchar eventos de notificación
        document.addEventListener('premium-ux:show-toast', (e) => {
            this.showToast(e.detail);
        });
    }

    /**
     * Mostrar notificación toast
     */
    showToast({ type = 'info', title, message, duration = 5000 }) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        toast.innerHTML = `
            <div class="toast-header">
                <h4 class="toast-title">${title}</h4>
                <button class="toast-close" aria-label="Cerrar notificación">&times;</button>
            </div>
            <p class="toast-message">${message}</p>
        `;
        
        this.toastContainer.appendChild(toast);
        
        // Animar entrada
        requestAnimationFrame(() => {
            toast.style.transform = 'translateX(0)';
        });
        
        // Configurar cierre
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            this.hideToast(toast);
        });
        
        // Auto-cerrar
        if (duration > 0) {
            setTimeout(() => {
                this.hideToast(toast);
            }, duration);
        }
        
        return toast;
    }

    /**
     * Ocultar notificación
     */
    hideToast(toast) {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    /**
     * Configurar sistema de modales
     */
    setupModals() {
        // Crear backdrop global
        this.modalBackdrop = document.createElement('div');
        this.modalBackdrop.className = 'modal-backdrop';
        document.body.appendChild(this.modalBackdrop);
        
        // Escuchar eventos de modal
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-modal-target]')) {
                e.preventDefault();
                const targetId = e.target.getAttribute('data-modal-target');
                this.showModal(targetId);
            }
            
            if (e.target.matches('[data-modal-close]')) {
                e.preventDefault();
                this.hideModal(e.target.closest('.modal'));
            }
        });
        
        // Cerrar con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModals.size > 0) {
                const lastModal = Array.from(this.activeModals).pop();
                this.hideModal(lastModal);
            }
        });
        
        // Cerrar con click en backdrop
        this.modalBackdrop.addEventListener('click', (e) => {
            if (e.target === this.modalBackdrop) {
                const lastModal = Array.from(this.activeModals).pop();
                this.hideModal(lastModal);
            }
        });
    }

    /**
     * Mostrar modal
     */
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        modal.classList.add('show');
        this.modalBackdrop.classList.add('show');
        this.activeModals.add(modal);
        
        // Focus en el modal
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
        
        // Trap focus
        this.trapFocus(modal);
        
        this.emit('premium-ux:modal-opened', { modalId });
    }

    /**
     * Ocultar modal
     */
    hideModal(modal) {
        if (!modal) return;
        
        modal.classList.remove('show');
        this.activeModals.delete(modal);
        
        if (this.activeModals.size === 0) {
            this.modalBackdrop.classList.remove('show');
        }
        
        this.emit('premium-ux:modal-closed', { modalId: modal.id });
    }

    /**
     * Trap focus en modal
     */
    trapFocus(modal) {
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        modal.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        });
    }

    /**
     * Configurar tooltips
     */
    setupTooltips() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.classList.add('tooltip');
            
            // Mejorar accesibilidad
            if (!element.hasAttribute('aria-label')) {
                element.setAttribute('aria-label', element.getAttribute('data-tooltip'));
            }
        });
    }

    /**
     * Configurar estados de carga
     */
    setupLoadingStates() {
        // Loading global
        document.addEventListener('premium-ux:show-loading', () => {
            this.showGlobalLoading();
        });
        
        document.addEventListener('premium-ux:hide-loading', () => {
            this.hideGlobalLoading();
        });
        
        // Loading de páginas
        this.setupPageLoading();
    }

    /**
     * Mostrar loading global
     */
    showGlobalLoading() {
        const loading = document.createElement('div');
        loading.className = 'global-loading';
        loading.innerHTML = `
            <div class="loading-spinner">
                <div class="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <p>Cargando...</p>
            </div>
        `;
        
        document.body.appendChild(loading);
        requestAnimationFrame(() => {
            loading.classList.add('show');
        });
    }

    /**
     * Ocultar loading global
     */
    hideGlobalLoading() {
        const loading = document.querySelector('.global-loading');
        if (loading) {
            loading.classList.remove('show');
            setTimeout(() => {
                if (loading.parentNode) {
                    loading.parentNode.removeChild(loading);
                }
            }, 300);
        }
    }

    /**
     * Configurar loading de páginas
     */
    setupPageLoading() {
        // Interceptar navegación
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (link && link.href && !link.href.startsWith('javascript:') && !link.href.startsWith('#')) {
                if (!link.hasAttribute('data-no-loading')) {
                    this.showPageLoading();
                }
            }
        });
        
        // Ocultar al cargar la página
        window.addEventListener('load', () => {
            this.hidePageLoading();
        });
    }

    /**
     * Mostrar loading de página
     */
    showPageLoading() {
        const loading = document.createElement('div');
        loading.className = 'page-loading';
        loading.innerHTML = '<div class="loading"></div>';
        document.body.appendChild(loading);
    }

    /**
     * Ocultar loading de página
     */
    hidePageLoading() {
        const loading = document.querySelector('.page-loading');
        if (loading) {
            loading.remove();
        }
    }

    /**
     * Configurar mejoras en formularios
     */
    setupFormEnhancements() {
        // Validación en tiempo real
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
            
            input.addEventListener('input', this.debounce(() => {
                this.validateField(input);
            }, 300));
        });
        
        // Auto-resize textareas
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', () => {
                this.autoResizeTextarea(textarea);
            });
        });
        
        // Mejorar selects
        this.enhanceSelects();
    }

    /**
     * Validar campo
     */
    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        
        // Limpiar estados previos
        field.classList.remove('is-valid', 'is-invalid');
        
        // Validar required
        if (required && !value) {
            field.classList.add('is-invalid');
            this.showFieldError(field, 'Este campo es requerido');
            return false;
        }
        
        // Validar email
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                field.classList.add('is-invalid');
                this.showFieldError(field, 'Email inválido');
                return false;
            }
        }
        
        // Validar teléfono
        if (type === 'tel' && value) {
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            if (!phoneRegex.test(value.replace(/\s/g, ''))) {
                field.classList.add('is-invalid');
                this.showFieldError(field, 'Teléfono inválido');
                return false;
            }
        }
        
        // Campo válido
        if (value) {
            field.classList.add('is-valid');
        }
        
        return true;
    }

    /**
     * Mostrar error de campo
     */
    showFieldError(field, message) {
        // Remover error previo
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Crear nuevo error
        const error = document.createElement('div');
        error.className = 'field-error';
        error.textContent = message;
        
        field.parentNode.appendChild(error);
    }

    /**
     * Auto-redimensionar textarea
     */
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    /**
     * Mejorar selects
     */
    enhanceSelects() {
        document.querySelectorAll('select').forEach(select => {
            const wrapper = document.createElement('div');
            wrapper.className = 'select-wrapper';
            
            select.parentNode.insertBefore(wrapper, select);
            wrapper.appendChild(select);
            
            // Agregar flecha personalizada
            const arrow = document.createElement('span');
            arrow.className = 'select-arrow';
            arrow.innerHTML = '▼';
            wrapper.appendChild(arrow);
        });
    }

    /**
     * Configurar navegación por teclado
     */
    setupKeyboardNavigation() {
        // Navegación por teclado mejorada
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K para búsqueda
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.openSearch();
            }
            
            // Ctrl/Cmd + / para ayuda
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                this.openHelp();
            }
        });
    }

    /**
     * Abrir búsqueda
     */
    openSearch() {
        this.emit('premium-ux:open-search');
    }

    /**
     * Abrir ayuda
     */
    openHelp() {
        this.emit('premium-ux:open-help');
    }

    /**
     * Configurar Intersection Observer
     */
    setupIntersectionObserver() {
        // Lazy loading de imágenes
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
        
        // Animaciones de scroll
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, { threshold: 0.1 });
        
        document.querySelectorAll('[data-animate-on-scroll]').forEach(el => {
            animationObserver.observe(el);
        });
    }

    /**
     * Configurar optimizaciones de rendimiento
     */
    setupPerformanceOptimizations() {
        // Debounce para eventos frecuentes
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 150));
        
        window.addEventListener('scroll', this.debounce(() => {
            this.handleScroll();
        }, 100));
        
        // Preload de recursos críticos
        this.preloadCriticalResources();
    }

    /**
     * Manejar resize
     */
    handleResize() {
        this.emit('premium-ux:resize', { width: window.innerWidth, height: window.innerHeight });
    }

    /**
     * Manejar scroll
     */
    handleScroll() {
        const scrollTop = window.pageYOffset;
        const scrollDirection = scrollTop > this.lastScrollTop ? 'down' : 'up';
        
        this.emit('premium-ux:scroll', { scrollTop, scrollDirection });
        
        this.lastScrollTop = scrollTop;
    }

    /**
     * Preload de recursos críticos
     */
    preloadCriticalResources() {
        const criticalImages = [
            '/static/images/logo.png',
            '/static/images/hero-bg.jpg'
        ];
        
        criticalImages.forEach(src => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'image';
            link.href = src;
            document.head.appendChild(link);
        });
    }

    /**
     * Función debounce
     */
    debounce(func, wait) {
        return (...args) => {
            clearTimeout(this.debounceTimers.get(func));
            this.debounceTimers.set(func, setTimeout(() => func.apply(this, args), wait));
        };
    }

    /**
     * Emitir eventos personalizados
     */
    emit(eventName, detail = {}) {
        const event = new CustomEvent(eventName, { detail });
        document.dispatchEvent(event);
    }

    /**
     * Obtener configuración
     */
    getConfig() {
        return {
            theme: this.currentTheme,
            animationsEnabled: this.animationsEnabled,
            accessibility: this.accessibilityConfig
        };
    }

    /**
     * Destruir instancia
     */
    destroy() {
        // Limpiar observers
        this.intersectionObservers.forEach(observer => observer.disconnect());
        this.intersectionObservers.clear();
        
        // Limpiar timers
        this.debounceTimers.forEach(timer => clearTimeout(timer));
        this.debounceTimers.clear();
        
        // Remover elementos del DOM
        if (this.toastContainer) {
            this.toastContainer.remove();
        }
        
        if (this.modalBackdrop) {
            this.modalBackdrop.remove();
        }
        
        this.isInitialized = false;
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.premiumUX = new PremiumUX();
    window.premiumUX.init();
});

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PremiumUX;
}
