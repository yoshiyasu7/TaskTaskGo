class NotificationService {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.toastContainer = null;
        this.initialized = false;

        this.config = {
            serverUrl: window.location.origin
        };

        // Ждем загрузки DOM перед инициализацией
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        if (this.initialized) return;

        this.createToastContainer();

        const token = this.getAuthToken();

        if (token) {
            console.log('NotificationService: Инициализация с токеном');
            this.initializeSocket();
        } else {
            console.log('NotificationService: Токен не найден, ожидание авторизации...');
            this.waitForAuth();
        }

        this.initialized = true;
    }

    createToastContainer() {
        if (!document.getElementById('toast-container')) {
            this.toastContainer = document.createElement('div');
            this.toastContainer.id = 'toast-container';

            // Проверяем, что body существует
            if (document.body) {
                document.body.appendChild(this.toastContainer);
            } else {
                // Если body еще не существует, ждем
                setTimeout(() => this.createToastContainer(), 100);
                return;
            }
        } else {
            this.toastContainer = document.getElementById('toast-container');
        }
    }

    waitForAuth() {
        const checkAuth = setInterval(() => {
            const token = this.getAuthToken();

            if (token) {
                console.log('NotificationService: Токен найден, запуск сервиса');
                clearInterval(checkAuth);
                this.initializeSocket();
            }
        }, 500);

        setTimeout(() => {
            clearInterval(checkAuth);
        }, 10000);
    }

    initializeSocket() {
        const token = this.getAuthToken();
        if (!token) {
            console.error('NotificationService: Токен не найден');
            return;
        }

        console.log('NotificationService: Установка подключения Socket.IO');
        this.socket = io(this.config.serverUrl, {
            auth: { token },
            transports: ['websocket', 'polling']
        });

        this.setupEventListeners();
    }

    setupEventListeners() {
        this.socket.on('connect', () => {
            console.log('NotificationService: Подключено к серверу');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            // Убрано уведомление о подключении
        });

        this.socket.on('disconnect', (reason) => {
            console.log('NotificationService: Отключено от сервера:', reason);
            this.isConnected = false;
            // Убрано уведомление об отключении
            this.attemptReconnect();
        });

        this.socket.on('connect_error', (error) => {
            console.error('NotificationService: Ошибка подключения:', error);
            // Убрано уведомление об ошибке подключения
            this.attemptReconnect();
        });

        this.socket.on('connected', (data) => {
            console.log('NotificationService: Успешная аутентификация');
        });

        this.socket.on('task_completed', (data) => {
            console.log('NotificationService: Получено уведомление о задаче:', data);
            this.handleTaskNotification(data);
        });
    }

    handleTaskNotification(data) {
        this.saveNotification(data);
        this.showBrowserNotification(data);
        this.showTaskToast(data);
        this.dispatchNotificationEvent(data);
    }

    showTaskToast(data) {
        const resultUrlHtml = data.result_url
            ? `<div><a href="${data.result_url}" target="_blank">Скачать результат</a></div>`
            : '';

        const toastHtml = `
            <div>
                <strong>Задача завершена!</strong>
                <div>${this.escapeHtml(data.task_title || 'Без названия')}</div>
                <div>${this.escapeHtml(data.message || 'Задача успешно завершена')}</div>
                ${resultUrlHtml}
            </div>
        `;

        this.showToast(toastHtml, 'success', 8080, true);
    }

    showToast(message, type = 'info', duration = 5000, isHtml = false) {
        // Убедимся, что контейнер существует
        if (!this.toastContainer) {
            this.createToastContainer();
        }

        if (!this.toastContainer) {
            console.warn('NotificationService: Контейнер для уведомлений не найден');
            return null;
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        if (isHtml) {
            toast.innerHTML = message;
        } else {
            toast.innerHTML = `<div>${message}</div>`;
        }

        this.toastContainer.appendChild(toast);

        if (duration > 0) {
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, duration);
        }

        return toast;
    }

    saveNotification(data) {
        try {
            const notifications = JSON.parse(localStorage.getItem('user_notifications') || '[]');
            const notification = {
                ...data,
                id: Date.now(),
                timestamp: new Date().toISOString(),
                read: false
            };

            notifications.unshift(notification);
            const limitedNotifications = notifications.slice(0, 100);
            localStorage.setItem('user_notifications', JSON.stringify(limitedNotifications));
            this.updateUnreadCount();

            console.log('NotificationService: Уведомление сохранено');
        } catch (error) {
            console.error('NotificationService: Ошибка сохранения уведомления:', error);
        }
    }

    updateUnreadCount() {
        try {
            const notifications = JSON.parse(localStorage.getItem('user_notifications') || '[]');
            const unreadCount = notifications.filter(n => !n.read).length;

            if (unreadCount > 0) {
                document.title = `(${unreadCount}) TaskTaskGo`;
            } else {
                document.title = 'TaskTaskGo';
            }

            window.dispatchEvent(new CustomEvent('notifications-count-updated', {
                detail: { count: unreadCount }
            }));
        } catch (error) {
            console.error('NotificationService: Ошибка обновления счетчика:', error);
        }
    }

    showBrowserNotification(data) {
        if (Notification.permission === 'granted') {
            const notification = new Notification('Задача завершена!', {
                body: data.message || `Задача "${data.task_title}" завершена`,
                icon: '/static/favicon.ico',
                tag: `task-${data.task_id}`
            });

            notification.onclick = () => {
                window.focus();
                if (window.location.pathname !== '/notifications') {
                    window.location.href = '/notifications';
                }
            };

            setTimeout(() => notification.close(), 5000);
        }
    }

    dispatchNotificationEvent(data) {
        const event = new CustomEvent('new-notification', {
            detail: data
        });
        window.dispatchEvent(event);
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`NotificationService: Попытка переподключения ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);

            setTimeout(() => {
                if (this.socket) {
                    this.socket.connect();
                }
            }, this.reconnectDelay);
        } else {
            console.error('NotificationService: Превышено максимальное количество попыток переподключения');
        }
    }

    getAuthToken() {
        return localStorage.getItem('tasktaskgo_jwt_token');
    }

    getNotifications() {
        try {
            return JSON.parse(localStorage.getItem('user_notifications') || '[]');
        } catch (error) {
            console.error('NotificationService: Ошибка получения уведомлений:', error);
            return [];
        }
    }

    markAsRead(notificationId) {
        try {
            const notifications = this.getNotifications();
            const updatedNotifications = notifications.map(notification =>
                notification.id === notificationId ? { ...notification, read: true } : notification
            );
            localStorage.setItem('user_notifications', JSON.stringify(updatedNotifications));
            this.updateUnreadCount();
        } catch (error) {
            console.error('NotificationService: Ошибка отметки как прочитанного:', error);
        }
    }

    markAllAsRead() {
        try {
            const notifications = this.getNotifications();
            const updatedNotifications = notifications.map(notification =>
                ({ ...notification, read: true })
            );
            localStorage.setItem('user_notifications', JSON.stringify(updatedNotifications));
            this.updateUnreadCount();
        } catch (error) {
            console.error('NotificationService: Ошибка отметки всех как прочитанных:', error);
        }
    }

    clearNotifications() {
        try {
            localStorage.removeItem('user_notifications');
            this.updateUnreadCount();
        } catch (error) {
            console.error('NotificationService: Ошибка очистки уведомлений:', error);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Создаем экземпляр только когда DOM готов
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.NotificationService = new NotificationService();
    });
} else {
    window.NotificationService = new NotificationService();
}