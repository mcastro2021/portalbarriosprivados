/**
 * Componente Dashboard Moderno
 * Maneja la funcionalidad del dashboard con actualizaciones en tiempo real
 */

class DashboardComponent {
    constructor() {
        this.socket = null;
        this.statsCache = new Map();
        this.updateInterval = null;
        this.isConnected = false;
        
        this.init();
    }
    
    init() {
        this.setupWebSocket();
        this.setupEventListeners();
        this.loadInitialData();
        this.startPeriodicUpdates();
    }
    
    setupWebSocket() {
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('Dashboard WebSocket conectado');
                this.isConnected = true;
                this.updateConnectionStatus(true);
            });
            
            this.socket.on('disconnect', () => {
                console.log('Dashboard WebSocket desconectado');
                this.isConnected = false;
                this.updateConnectionStatus(false);
            });
            
            this.socket.on('notification', (data) => {
                this.handleNewNotification(data);
            });
            
            this.socket.on('stats_update', (data) => {
                this.updateStats(data);
            });
            
            this.socket.on('activity_update', (data) => {
                this.addActivity(data);
            });
        }
    }
    
    setupEventListeners() {
        // Botón de actualizar stats
        const refreshBtn = document.getElementById('refresh-stats');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshStats());
        }
        
        // Notificaciones
        const notificationBell = document.getElementById('notification-bell');
        if (notificationBell) {
            notificationBell.addEventListener('click', () => this.toggleNotifications());
        }
        
        // Marcar todas las notificaciones como leídas
        const markAllReadBtn = document.getElementById('mark-all-read');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', () => this.markAllNotificationsRead());
        }
        
        // Cards interactivos
        this.setupInteractiveCards();
    }
    
    setupInteractiveCards() {
        const cards = document.querySelectorAll('.dashboard-card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.classList.add('card-hover');
            });
            
            card.addEventListener('mouseleave', () => {
                card.classList.remove('card-hover');
            });
            
            // Animación de click
            card.addEventListener('click', (e) => {
                if (!e.target.closest('a, button')) {
                    this.animateCard(card);
                }
            });
        });
    }
    
    animateCard(card) {
        card.style.transform = 'scale(0.98)';
        setTimeout(() => {
            card.style.transform = 'scale(1)';
        }, 150);
    }
    
    async loadInitialData() {
        try {
            this.showLoading(true);
            
            // Cargar estadísticas
            const statsResponse = await fetch('/api/v1/dashboard/stats');
            if (statsResponse.ok) {
                const stats = await statsResponse.json();
                this.updateStats(stats);
            }
            
            // Cargar actividades recientes
            await this.loadRecentActivities();
            
            // Cargar notificaciones
            await this.loadNotifications();
            
        } catch (error) {
            console.error('Error cargando datos iniciales:', error);
            this.showError('Error cargando datos del dashboard');
        } finally {
            this.showLoading(false);
        }
    }
    
    async loadRecentActivities() {
        try {
            const response = await fetch('/api/v1/dashboard/activities');
            if (response.ok) {
                const activities = await response.json();
                this.renderActivities(activities);
            }
        } catch (error) {
            console.error('Error cargando actividades:', error);
        }
    }
    
    async loadNotifications() {
        try {
            const response = await fetch('/api/v1/notifications?limit=5');
            if (response.ok) {
                const notifications = await response.json();
                this.renderNotifications(notifications);
                this.updateNotificationBadge(notifications.unread_count || 0);
            }
        } catch (error) {
            console.error('Error cargando notificaciones:', error);
        }
    }
    
    updateStats(stats) {
        // Actualizar contadores con animación
        Object.entries(stats).forEach(([key, value]) => {
            const element = document.getElementById(`stat-${key.replace('_', '-')}`);
            if (element) {
                this.animateCounter(element, parseInt(value) || 0);
            }
        });
        
        // Guardar en cache
        this.statsCache.set('current', { ...stats, timestamp: Date.now() });
    }
    
    animateCounter(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const increment = Math.ceil((targetValue - currentValue) / 20);
        
        if (increment === 0) return;
        
        const timer = setInterval(() => {
            const current = parseInt(element.textContent) || 0;
            const newValue = current + increment;
            
            if ((increment > 0 && newValue >= targetValue) || 
                (increment < 0 && newValue <= targetValue)) {
                element.textContent = targetValue;
                clearInterval(timer);
            } else {
                element.textContent = newValue;
            }
        }, 50);
    }
    
    renderActivities(activities) {
        const container = document.getElementById('recent-activities');
        if (!container) return;
        
        if (!activities || activities.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay actividades recientes</p>';
            return;
        }
        
        const html = activities.map(activity => `
            <div class="activity-item" data-activity-id="${activity.id}">
                <div class="activity-icon">
                    <i class="${activity.icon} text-${activity.color}"></i>
                </div>
                <div class="activity-content">
                    <h6 class="activity-title">${activity.title}</h6>
                    <p class="activity-description">${activity.description}</p>
                    <small class="activity-time text-muted">
                        ${this.formatTimeAgo(activity.timestamp)}
                    </small>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    renderNotifications(notifications) {
        const container = document.getElementById('notifications-list');
        if (!container) return;
        
        if (!notifications.items || notifications.items.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay notificaciones</p>';
            return;
        }
        
        const html = notifications.items.map(notification => `
            <div class="notification-item ${notification.is_read ? '' : 'unread'}" 
                 data-notification-id="${notification.id}">
                <div class="notification-content">
                    <h6 class="notification-title">${notification.title}</h6>
                    <p class="notification-message">${notification.message}</p>
                    <small class="notification-time text-muted">
                        ${this.formatTimeAgo(notification.created_at)}
                    </small>
                </div>
                ${!notification.is_read ? '<div class="notification-badge"></div>' : ''}
            </div>
        `).join('');
        
        container.innerHTML = html;
        
        // Agregar event listeners para marcar como leída
        container.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', () => {
                const notificationId = item.dataset.notificationId;
                this.markNotificationRead(notificationId);
            });
        });
    }
    
    handleNewNotification(notification) {
        // Mostrar toast de notificación
        this.showNotificationToast(notification);
        
        // Actualizar badge
        const currentBadge = document.getElementById('notification-badge');
        if (currentBadge) {
            const currentCount = parseInt(currentBadge.textContent) || 0;
            this.updateNotificationBadge(currentCount + 1);
        }
        
        // Agregar a la lista si está visible
        const container = document.getElementById('notifications-list');
        if (container && container.style.display !== 'none') {
            this.prependNotification(notification);
        }
    }
    
    showNotificationToast(notification) {
        // Crear toast personalizado
        const toast = document.createElement('div');
        toast.className = 'notification-toast';
        toast.innerHTML = `
            <div class="toast-header">
                <i class="fas fa-bell text-primary"></i>
                <strong class="me-auto">${notification.title}</strong>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
            <div class="toast-body">
                ${notification.content || notification.message}
            </div>
        `;
        
        // Agregar al contenedor de toasts
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        
        // Auto-remove después de 5 segundos
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }
    
    async markNotificationRead(notificationId) {
        try {
            const response = await fetch(`/api/v1/notifications/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                // Actualizar UI
                const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
                if (notificationElement) {
                    notificationElement.classList.remove('unread');
                    const badge = notificationElement.querySelector('.notification-badge');
                    if (badge) badge.remove();
                }
                
                // Actualizar contador
                this.decrementNotificationBadge();
            }
        } catch (error) {
            console.error('Error marcando notificación como leída:', error);
        }
    }
    
    async markAllNotificationsRead() {
        try {
            const response = await fetch('/api/v1/notifications/mark-all-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                // Actualizar UI
                document.querySelectorAll('.notification-item.unread').forEach(item => {
                    item.classList.remove('unread');
                    const badge = item.querySelector('.notification-badge');
                    if (badge) badge.remove();
                });
                
                // Resetear badge
                this.updateNotificationBadge(0);
            }
        } catch (error) {
            console.error('Error marcando todas las notificaciones:', error);
        }
    }
    
    updateNotificationBadge(count) {
        const badge = document.getElementById('notification-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    }
    
    decrementNotificationBadge() {
        const badge = document.getElementById('notification-badge');
        if (badge) {
            const currentCount = parseInt(badge.textContent) || 0;
            this.updateNotificationBadge(Math.max(0, currentCount - 1));
        }
    }
    
    addActivity(activity) {
        const container = document.getElementById('recent-activities');
        if (!container) return;
        
        // Crear elemento de actividad
        const activityElement = document.createElement('div');
        activityElement.className = 'activity-item new-activity';
        activityElement.innerHTML = `
            <div class="activity-icon">
                <i class="${activity.icon} text-${activity.color}"></i>
            </div>
            <div class="activity-content">
                <h6 class="activity-title">${activity.title}</h6>
                <p class="activity-description">${activity.description}</p>
                <small class="activity-time text-muted">Ahora</small>
            </div>
        `;
        
        // Insertar al principio
        container.insertBefore(activityElement, container.firstChild);
        
        // Remover clase de nueva actividad después de la animación
        setTimeout(() => {
            activityElement.classList.remove('new-activity');
        }, 1000);
        
        // Limitar número de actividades mostradas
        const activities = container.querySelectorAll('.activity-item');
        if (activities.length > 10) {
            activities[activities.length - 1].remove();
        }
    }
    
    async refreshStats() {
        const refreshBtn = document.getElementById('refresh-stats');
        if (refreshBtn) {
            refreshBtn.classList.add('spinning');
        }
        
        try {
            await this.loadInitialData();
        } finally {
            if (refreshBtn) {
                refreshBtn.classList.remove('spinning');
            }
        }
    }
    
    startPeriodicUpdates() {
        // Actualizar cada 30 segundos
        this.updateInterval = setInterval(() => {
            if (document.visibilityState === 'visible') {
                this.refreshStats();
            }
        }, 30000);
    }
    
    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connection-status');
        if (statusIndicator) {
            statusIndicator.className = connected ? 'status-connected' : 'status-disconnected';
            statusIndicator.title = connected ? 'Conectado' : 'Desconectado';
        }
    }
    
    toggleNotifications() {
        const dropdown = document.getElementById('notifications-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    }
    
    showLoading(show) {
        const loader = document.getElementById('dashboard-loader');
        if (loader) {
            loader.style.display = show ? 'block' : 'none';
        }
    }
    
    showError(message) {
        // Mostrar error toast
        const toast = document.createElement('div');
        toast.className = 'error-toast';
        toast.innerHTML = `
            <div class="toast-header bg-danger text-white">
                <i class="fas fa-exclamation-triangle"></i>
                <strong class="me-auto">Error</strong>
                <button type="button" class="btn-close btn-close-white" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }
    
    formatTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);
        
        if (diffInSeconds < 60) {
            return 'Hace un momento';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `Hace ${hours} hora${hours > 1 ? 's' : ''}`;
        } else {
            const days = Math.floor(diffInSeconds / 86400);
            return `Hace ${days} día${days > 1 ? 's' : ''}`;
        }
    }
    
    destroy() {
        if (this.socket) {
            this.socket.disconnect();
        }
        
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardComponent = new DashboardComponent();
});

// Limpiar al salir de la página
window.addEventListener('beforeunload', () => {
    if (window.dashboardComponent) {
        window.dashboardComponent.destroy();
    }
});
