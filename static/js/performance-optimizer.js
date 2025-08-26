/**
 * Optimizador de Performance Frontend
 * Lazy loading, virtual scrolling y optimización de assets
 */

class PerformanceOptimizer {
    constructor() {
        this.intersectionObserver = null;
        this.lazyComponents = new Map();
        this.virtualLists = new Map();
        this.assetCache = new Map();
        this.init();
    }

    init() {
        this.setupIntersectionObserver();
        this.setupLazyLoading();
        this.setupVirtualScrolling();
        this.setupAssetOptimization();
        this.setupPerformanceMonitoring();
    }

    /**
     * Configurar Intersection Observer para lazy loading
     */
    setupIntersectionObserver() {
        this.intersectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = entry.target;
                    const componentId = target.dataset.lazyComponent;
                    
                    if (componentId && this.lazyComponents.has(componentId)) {
                        this.loadComponent(componentId, target);
                    }
                }
            });
        }, {
            rootMargin: '50px',
            threshold: 0.1
        });
    }

    /**
     * Configurar lazy loading para componentes
     */
    setupLazyLoading() {
        // Registrar componentes lazy
        this.registerLazyComponent('map', () => this.loadMapComponent());
        this.registerLazyComponent('calendar', () => this.loadCalendarComponent());
        this.registerLazyComponent('chatbot', () => this.loadChatbotComponent());
        this.registerLazyComponent('notifications', () => this.loadNotificationsComponent());
        this.registerLazyComponent('statistics', () => this.loadStatisticsComponent());
        
        // Observar elementos con lazy loading
        document.querySelectorAll('[data-lazy-component]').forEach(element => {
            this.intersectionObserver.observe(element);
        });
    }

    /**
     * Registrar componente lazy
     */
    registerLazyComponent(id, loader) {
        this.lazyComponents.set(id, {
            loader,
            loaded: false,
            element: null
        });
    }

    /**
     * Cargar componente lazy
     */
    async loadComponent(componentId, element) {
        const component = this.lazyComponents.get(componentId);
        if (!component || component.loaded) return;

        try {
            element.innerHTML = '<div class="loading-spinner">Cargando...</div>';
            
            const result = await component.loader();
            element.innerHTML = result;
            component.loaded = true;
            component.element = element;
            
            // Disparar evento de componente cargado
            element.dispatchEvent(new CustomEvent('componentLoaded', {
                detail: { componentId }
            }));
            
        } catch (error) {
            console.error(`Error cargando componente ${componentId}:`, error);
            element.innerHTML = '<div class="error-message">Error al cargar componente</div>';
        }
    }

    /**
     * Cargar componente de mapa
     */
    async loadMapComponent() {
        // Lazy load de Leaflet
        await this.loadScript('/static/js/leaflet.js');
        await this.loadCSS('/static/css/leaflet.css');
        
        return `
            <div id="interactive-map" class="map-container">
                <div id="map" style="height: 400px;"></div>
                <script>
                    // Inicializar mapa después de cargar
                    document.addEventListener('DOMContentLoaded', function() {
                        if (typeof L !== 'undefined') {
                            const map = L.map('map').setView([-34.6037, -58.3816], 13);
                            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
                        }
                    });
                </script>
            </div>
        `;
    }

    /**
     * Cargar componente de calendario
     */
    async loadCalendarComponent() {
        await this.loadScript('/static/js/fullcalendar.js');
        await this.loadCSS('/static/css/fullcalendar.css');
        
        return `
            <div id="calendar-container">
                <div id="calendar"></div>
                <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        if (typeof FullCalendar !== 'undefined') {
                            const calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
                                initialView: 'dayGridMonth',
                                locale: 'es',
                                headerToolbar: {
                                    left: 'prev,next today',
                                    center: 'title',
                                    right: 'dayGridMonth,timeGridWeek,timeGridDay'
                                }
                            });
                            calendar.render();
                        }
                    });
                </script>
            </div>
        `;
    }

    /**
     * Cargar componente de chatbot
     */
    async loadChatbotComponent() {
        return `
            <div id="chatbot-container" class="chatbot-widget">
                <div class="chatbot-header">
                    <h4>Asistente Virtual</h4>
                    <button class="chatbot-toggle" onclick="toggleChatbot()">
                        <i class="fas fa-comments"></i>
                    </button>
                </div>
                <div class="chatbot-body" style="display: none;">
                    <div id="chat-messages"></div>
                    <div class="chat-input">
                        <input type="text" id="chat-input" placeholder="Escribe tu pregunta...">
                        <button onclick="sendChatMessage()">Enviar</button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Cargar componente de notificaciones
     */
    async loadNotificationsComponent() {
        return `
            <div id="notifications-container">
                <div class="notifications-header">
                    <h4>Notificaciones</h4>
                    <button onclick="markAllAsRead()">Marcar todas como leídas</button>
                </div>
                <div id="notifications-list" class="notifications-list">
                    <!-- Las notificaciones se cargarán dinámicamente -->
                </div>
            </div>
        `;
    }

    /**
     * Cargar componente de estadísticas
     */
    async loadStatisticsComponent() {
        await this.loadScript('/static/js/chart.js');
        
        return `
            <div id="statistics-container">
                <div class="stats-grid">
                    <div class="stat-card">
                        <h5>Visitas Pendientes</h5>
                        <div id="pending-visits-chart"></div>
                    </div>
                    <div class="stat-card">
                        <h5>Reservas Activas</h5>
                        <div id="active-reservations-chart"></div>
                    </div>
                </div>
                <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        if (typeof Chart !== 'undefined') {
                            loadStatisticsCharts();
                        }
                    });
                </script>
            </div>
        `;
    }

    /**
     * Configurar virtual scrolling para listas largas
     */
    setupVirtualScrolling() {
        // Implementar virtual scrolling para listas largas
        document.querySelectorAll('[data-virtual-scroll]').forEach(container => {
            this.createVirtualList(container);
        });
    }

    /**
     * Crear lista virtual
     */
    createVirtualList(container) {
        const itemHeight = parseInt(container.dataset.itemHeight) || 50;
        const totalItems = parseInt(container.dataset.totalItems) || 0;
        const visibleItems = Math.ceil(container.clientHeight / itemHeight);
        
        const virtualList = {
            container,
            itemHeight,
            totalItems,
            visibleItems,
            scrollTop: 0,
            startIndex: 0,
            endIndex: visibleItems
        };
        
        this.virtualLists.set(container.id, virtualList);
        
        // Configurar scroll event
        container.addEventListener('scroll', (e) => {
            this.updateVirtualList(virtualList, e.target.scrollTop);
        });
        
        // Renderizar items iniciales
        this.renderVirtualItems(virtualList);
    }

    /**
     * Actualizar lista virtual
     */
    updateVirtualList(virtualList, scrollTop) {
        const { itemHeight, totalItems, visibleItems } = virtualList;
        
        const startIndex = Math.floor(scrollTop / itemHeight);
        const endIndex = Math.min(startIndex + visibleItems, totalItems);
        
        if (startIndex !== virtualList.startIndex || endIndex !== virtualList.endIndex) {
            virtualList.startIndex = startIndex;
            virtualList.endIndex = endIndex;
            virtualList.scrollTop = scrollTop;
            
            this.renderVirtualItems(virtualList);
        }
    }

    /**
     * Renderizar items de lista virtual
     */
    renderVirtualItems(virtualList) {
        const { container, itemHeight, startIndex, endIndex } = virtualList;
        
        // Crear contenedor de items
        let itemsContainer = container.querySelector('.virtual-items');
        if (!itemsContainer) {
            itemsContainer = document.createElement('div');
            itemsContainer.className = 'virtual-items';
            container.appendChild(itemsContainer);
        }
        
        // Calcular altura del contenedor
        const totalHeight = virtualList.totalItems * itemHeight;
        itemsContainer.style.height = `${totalHeight}px`;
        
        // Renderizar solo items visibles
        itemsContainer.innerHTML = '';
        for (let i = startIndex; i < endIndex; i++) {
            const item = this.createVirtualItem(i);
            item.style.position = 'absolute';
            item.style.top = `${i * itemHeight}px`;
            item.style.height = `${itemHeight}px`;
            itemsContainer.appendChild(item);
        }
    }

    /**
     * Crear item de lista virtual
     */
    createVirtualItem(index) {
        // Esta función debe ser personalizada según el tipo de datos
        const item = document.createElement('div');
        item.className = 'virtual-item';
        item.textContent = `Item ${index + 1}`;
        return item;
    }

    /**
     * Configurar optimización de assets
     */
    setupAssetOptimization() {
        // Precargar assets críticos
        this.preloadCriticalAssets();
        
        // Optimizar imágenes
        this.optimizeImages();
        
        // Comprimir CSS y JS
        this.compressAssets();
    }

    /**
     * Precargar assets críticos
     */
    preloadCriticalAssets() {
        const criticalAssets = [
            '/static/css/app.css',
            '/static/js/app.js',
            '/static/images/logo.png'
        ];
        
        criticalAssets.forEach(asset => {
            if (asset.endsWith('.css')) {
                this.preloadCSS(asset);
            } else if (asset.endsWith('.js')) {
                this.preloadScript(asset);
            } else if (asset.endsWith('.png') || asset.endsWith('.jpg')) {
                this.preloadImage(asset);
            }
        });
    }

    /**
     * Optimizar imágenes
     */
    optimizeImages() {
        // Lazy loading para imágenes
        const images = document.querySelectorAll('img[data-src]');
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
        
        images.forEach(img => imageObserver.observe(img));
    }

    /**
     * Comprimir assets
     */
    compressAssets() {
        // Comprimir CSS inline
        const styleSheets = document.styleSheets;
        for (let i = 0; i < styleSheets.length; i++) {
            const sheet = styleSheets[i];
            if (sheet.href) {
                this.compressCSS(sheet.href);
            }
        }
    }

    /**
     * Configurar monitoreo de performance
     */
    setupPerformanceMonitoring() {
        // Monitorear métricas de performance
        this.monitorPerformanceMetrics();
        
        // Monitorear errores
        this.monitorErrors();
        
        // Monitorear tiempo de carga
        this.monitorLoadTimes();
    }

    /**
     * Monitorear métricas de performance
     */
    monitorPerformanceMetrics() {
        if ('performance' in window) {
            window.addEventListener('load', () => {
                const perfData = performance.getEntriesByType('navigation')[0];
                
                const metrics = {
                    loadTime: perfData.loadEventEnd - perfData.loadEventStart,
                    domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                    firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime,
                    firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime
                };
                
                // Enviar métricas al servidor
                this.sendPerformanceMetrics(metrics);
            });
        }
    }

    /**
     * Monitorear errores
     */
    monitorErrors() {
        window.addEventListener('error', (event) => {
            this.logError('JavaScript Error', {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                stack: event.error?.stack
            });
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            this.logError('Unhandled Promise Rejection', {
                reason: event.reason
            });
        });
    }

    /**
     * Monitorear tiempo de carga
     */
    monitorLoadTimes() {
        const observer = new PerformanceObserver((list) => {
            list.getEntries().forEach((entry) => {
                if (entry.entryType === 'measure') {
                    console.log(`${entry.name}: ${entry.duration}ms`);
                }
            });
        });
        
        observer.observe({ entryTypes: ['measure'] });
    }

    /**
     * Utilidades para cargar assets
     */
    async loadScript(src) {
        if (this.assetCache.has(src)) {
            return this.assetCache.get(src);
        }
        
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = () => {
                this.assetCache.set(src, true);
                resolve();
            };
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    async loadCSS(href) {
        if (this.assetCache.has(href)) {
            return this.assetCache.get(href);
        }
        
        return new Promise((resolve, reject) => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.onload = () => {
                this.assetCache.set(href, true);
                resolve();
            };
            link.onerror = reject;
            document.head.appendChild(link);
        });
    }

    preloadCSS(href) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'style';
        link.href = href;
        document.head.appendChild(link);
    }

    preloadScript(src) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'script';
        link.href = src;
        document.head.appendChild(link);
    }

    preloadImage(src) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'image';
        link.href = src;
        document.head.appendChild(link);
    }

    /**
     * Enviar métricas de performance al servidor
     */
    async sendPerformanceMetrics(metrics) {
        try {
            await fetch('/api/performance-metrics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(metrics)
            });
        } catch (error) {
            console.error('Error enviando métricas:', error);
        }
    }

    /**
     * Log de errores
     */
    async logError(type, details) {
        try {
            await fetch('/api/log-error', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type,
                    details,
                    timestamp: new Date().toISOString(),
                    userAgent: navigator.userAgent,
                    url: window.location.href
                })
            });
        } catch (error) {
            console.error('Error logging error:', error);
        }
    }
}

// Inicializar optimizador cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.performanceOptimizer = new PerformanceOptimizer();
});

// Funciones globales para componentes
window.toggleChatbot = function() {
    const body = document.querySelector('.chatbot-body');
    body.style.display = body.style.display === 'none' ? 'block' : 'none';
};

window.sendChatMessage = function() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (message) {
        // Enviar mensaje al chatbot
        fetch('/api/chatbot/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            // Mostrar respuesta
            const messagesContainer = document.getElementById('chat-messages');
            messagesContainer.innerHTML += `
                <div class="chat-message user">${message}</div>
                <div class="chat-message bot">${data.response}</div>
            `;
            input.value = '';
        });
    }
};

window.markAllAsRead = function() {
    fetch('/api/notifications/mark-all-read', {
        method: 'POST'
    })
    .then(() => {
        // Actualizar UI
        document.querySelectorAll('.notification-item').forEach(item => {
            item.classList.remove('unread');
        });
    });
};
