// Main JavaScript for Portal Barrio Privado

// Helper function to handle API responses
function handleApiResponse(response) {
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
        // If not JSON, user is probably not authenticated
        throw new Error('User not authenticated');
    }
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
}

// Initialize Socket.IO connection
let socket = null;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeNotifications();
    initializeChatbot();
    initializeCharts();
    initializeForms();
    initializeModals();
});

// Socket.IO initialization
function initializeSocket() {
    if (typeof io !== 'undefined') {
        socket = io();
        
        socket.on('connect', function() {
            console.log('Connected to server');
            updateConnectionStatus(true);
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from server');
            updateConnectionStatus(false);
        });
        
        // Listen for notifications
        socket.on('notification', function(data) {
            showNotification(data);
            updateNotificationCount();
        });
        
        // Listen for visit updates
        socket.on('visit_update', function(data) {
            updateVisitStatus(data);
        });
        
        // Listen for reservation updates
        socket.on('reservation_update', function(data) {
            updateReservationStatus(data);
        });
        
        // Listen for maintenance updates
        socket.on('maintenance_update', function(data) {
            updateMaintenanceStatus(data);
        });
        
        // Listen for security alerts
        socket.on('security_alert', function(data) {
            showSecurityAlert(data);
        });
    }
}

// Update connection status indicator
function updateConnectionStatus(connected) {
    const statusIndicator = document.getElementById('connection-status');
    if (statusIndicator) {
        statusIndicator.className = connected ? 'badge bg-success' : 'badge bg-danger';
        statusIndicator.textContent = connected ? 'Conectado' : 'Desconectado';
    }
}

// Notification system
function initializeNotifications() {
    // Update notification count on page load
    updateNotificationCount();
    
    // Mark notifications as read when clicked
    document.addEventListener('click', function(e) {
        if (e.target.closest('.notification-item')) {
            const notificationId = e.target.closest('.notification-item').dataset.id;
            markNotificationAsRead(notificationId);
        }
    });
}

function updateNotificationCount() {
    fetch('/api/notifications/count')
        .then(handleApiResponse)
        .then(data => {
            const countElement = document.getElementById('notification-count');
            if (countElement) {
                countElement.textContent = data.count;
                countElement.style.display = data.count > 0 ? 'inline' : 'none';
            }
        })
        .catch(error => {
            // Silently handle authentication issues - user is not logged in
            if (error.message === 'User not authenticated') {
                // Hide notification count for unauthenticated users
                const countElement = document.getElementById('notification-count');
                if (countElement) {
                    countElement.style.display = 'none';
                }
            } else {
                console.error('Error updating notification count:', error);
            }
        });
}

function showNotification(data) {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-primary border-0';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-bell me-2"></i>
                ${data.message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to toast container
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
    
    // Update notification count
    updateNotificationCount();
}

function markNotificationAsRead(notificationId) {
    fetch(`/api/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(handleApiResponse)
    .then(data => {
        if (data.success) {
            const notificationElement = document.querySelector(`[data-id="${notificationId}"]`);
            if (notificationElement) {
                notificationElement.classList.remove('unread');
            }
            updateNotificationCount();
        }
    })
    .catch(error => {
        // Only log as error if it's not an authentication issue
        if (error.message !== 'User not authenticated') {
            console.error('Error marking notification as read:', error);
        }
    });
}

// Chatbot functionality
function initializeChatbot() {
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotClose = document.getElementById('chatbot-close');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotSend = document.getElementById('chatbot-send');
    
    if (chatbotToggle && chatbotWindow) {
        chatbotToggle.addEventListener('click', function() {
            chatbotWindow.style.display = chatbotWindow.style.display === 'flex' ? 'none' : 'flex';
        });
        
        if (chatbotClose) {
            chatbotClose.addEventListener('click', function() {
                chatbotWindow.style.display = 'none';
            });
        }
        
        if (chatbotSend && chatbotInput) {
            chatbotSend.addEventListener('click', sendChatbotMessage);
            chatbotInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendChatbotMessage();
                }
            });
        }
    }
}

function sendChatbotMessage() {
    const input = document.getElementById('chatbot-input');
    const messages = document.getElementById('chatbot-messages');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addChatbotMessage('user', message);
    input.value = '';
    
    // Send to server
    fetch('/api/chatbot/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(handleApiResponse)
    .then(data => {
        addChatbotMessage('bot', data.response);
    })
    .catch(error => {
        if (error.message === 'User not authenticated') {
            addChatbotMessage('bot', 'Por favor, inicia sesión para usar el chatbot.');
        } else {
            console.error('Error sending chatbot message:', error);
            addChatbotMessage('bot', 'Lo siento, hubo un error. Inténtalo de nuevo.');
        }
    });
}

function addChatbotMessage(sender, message) {
    const messages = document.getElementById('chatbot-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `mb-2 ${sender === 'user' ? 'text-end' : 'text-start'}`;
    
    const messageBubble = document.createElement('div');
    messageBubble.className = `d-inline-block p-2 rounded ${sender === 'user' ? 'bg-primary text-white' : 'bg-light'}`;
    messageBubble.style.maxWidth = '80%';
    messageBubble.textContent = message;
    
    messageDiv.appendChild(messageBubble);
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

// Charts initialization
function initializeCharts() {
    // Dashboard charts
    const visitChart = document.getElementById('visit-chart');
    if (visitChart) {
        new Chart(visitChart, {
            type: 'line',
            data: {
                labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
                datasets: [{
                    label: 'Visitas',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    const expenseChart = document.getElementById('expense-chart');
    if (expenseChart) {
        new Chart(expenseChart, {
            type: 'doughnut',
            data: {
                labels: ['Pagadas', 'Pendientes', 'Vencidas'],
                datasets: [{
                    data: [70, 20, 10],
                    backgroundColor: [
                        'rgb(75, 192, 192)',
                        'rgb(255, 205, 86)',
                        'rgb(255, 99, 132)'
                    ]
                }]
            },
            options: {
                responsive: true
            }
        });
    }
}

// Form handling
function initializeForms() {
    // Auto-save forms
    const forms = document.querySelectorAll('form[data-autosave]');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                saveFormData(form);
            });
        });
    });
    
    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            previewFile(this);
        });
    });
    
    // Form validation
    const formsWithValidation = document.querySelectorAll('form[data-validate]');
    formsWithValidation.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function saveFormData(form) {
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem(`form_${form.id}`, JSON.stringify(data));
}

function loadFormData(form) {
    const saved = localStorage.getItem(`form_${form.id}`);
    if (saved) {
        const data = JSON.parse(saved);
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = data[key];
            }
        });
    }
}

function previewFile(input) {
    const preview = document.getElementById('file-preview');
    if (preview && input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Modal handling
function initializeModals() {
    // Auto-focus on first input in modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = this.querySelector('input, textarea, select');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });
}

// Utility functions
function showLoading(element) {
    element.innerHTML = '<div class="spinner mx-auto"></div>';
}

function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS'
    }).format(amount);
}

// Update functions for real-time data
function updateVisitStatus(data) {
    const visitElement = document.querySelector(`[data-visit-id="${data.visit_id}"]`);
    if (visitElement) {
        const statusElement = visitElement.querySelector('.visit-status');
        if (statusElement) {
            statusElement.textContent = data.status;
            statusElement.className = `badge ${getStatusClass(data.status)}`;
        }
    }
}

function updateReservationStatus(data) {
    const reservationElement = document.querySelector(`[data-reservation-id="${data.reservation_id}"]`);
    if (reservationElement) {
        const statusElement = reservationElement.querySelector('.reservation-status');
        if (statusElement) {
            statusElement.textContent = data.status;
            statusElement.className = `badge ${getStatusClass(data.status)}`;
        }
    }
}

function updateMaintenanceStatus(data) {
    const maintenanceElement = document.querySelector(`[data-maintenance-id="${data.maintenance_id}"]`);
    if (maintenanceElement) {
        const statusElement = maintenanceElement.querySelector('.maintenance-status');
        if (statusElement) {
            statusElement.textContent = data.status;
            statusElement.className = `badge ${getStatusClass(data.status)}`;
        }
    }
}

function getStatusClass(status) {
    const statusClasses = {
        'pending': 'bg-warning',
        'in_progress': 'bg-info',
        'completed': 'bg-success',
        'cancelled': 'bg-danger',
        'approved': 'bg-success',
        'rejected': 'bg-danger'
    };
    return statusClasses[status] || 'bg-secondary';
}

function showSecurityAlert(data) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        <i class="bi bi-exclamation-triangle me-2"></i>
        <strong>Alerta de Seguridad:</strong> ${data.message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.insertBefore(alert, container.firstChild);
    }
}

// Export functions for use in other scripts
window.PortalApp = {
    showNotification,
    updateNotificationCount,
    formatDate,
    formatCurrency,
    showLoading,
    hideLoading
}; 