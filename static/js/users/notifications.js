document.addEventListener('DOMContentLoaded', function() {
    initializeNotificationsPage();
});

function initializeNotificationsPage() {
    console.log('NotificationsPage: Инициализация страницы уведомлений');

    // Загружаем историю уведомлений
    loadNotificationHistory();

    // Слушаем новые уведомления от сервиса
    window.addEventListener('new-notification', (event) => {
        console.log('NotificationsPage: Получено новое уведомление', event.detail);
        displayTaskNotification(event.detail);
    });

    // Добавляем обработчики кнопок
    setupEventHandlers();
}

function loadNotificationHistory() {
    const notifications = window.NotificationService.getNotifications();
    const notificationsDiv = document.getElementById('notifications');

    // Очищаем контейнер, но оставляем заголовок
    const existingNotifications = notificationsDiv.querySelectorAll('.notification');
    existingNotifications.forEach(el => el.remove());

    if (notifications.length === 0) {
        notificationsDiv.innerHTML += '<p class="no-notifications">Пока нет уведомлений</p>';
        return;
    }

    notifications.forEach(notification => {
        const element = createNotificationElement(notification);
        notificationsDiv.appendChild(element);
    });

    // Отмечаем все как прочитанные при загрузке страницы
    window.NotificationService.markAllAsRead();
}

function displayTaskNotification(data) {
    const notificationsDiv = document.getElementById('notifications');

    // Убираем сообщение "нет уведомлений"
    const noNotifications = notificationsDiv.querySelector('.no-notifications');
    if (noNotifications) {
        noNotifications.remove();
    }

    const notification = createNotificationElement({
        ...data,
        id: Date.now(),
        timestamp: new Date().toISOString()
    });

    // Добавляем в начало с анимацией
    notificationsDiv.insertBefore(notification, notificationsDiv.firstChild);

    // Анимация появления
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(-20px)';

    setTimeout(() => {
        notification.style.transition = 'all 0.3s ease';
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 10);

    // Прокручиваем к новому уведомлению
    notification.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Ограничиваем количество уведомлений
    limitNotifications(50);
}

function createNotificationElement(data) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.dataset.id = data.id;

    const resultUrlHtml = data.result_url
        ? `<p><strong>Результат:</strong> <a href="${data.result_url}" target="_blank" class="result-link">Скачать результат</a></p>`
        : '';

    const time = new Date(data.timestamp || Date.now()).toLocaleString('ru-RU');

    notification.innerHTML = `
        <div class="notification-header">
            <h3>✅ Задача завершена!</h3>
            <span class="notification-time">${time}</span>
        </div>
        <div class="notification-body">
            <p><strong>Название:</strong> ${escapeHtml(data.task_title || 'Без названия')}</p>
            <p><strong>ID задачи:</strong> ${data.task_id}</p>
            ${resultUrlHtml}
            <p><strong>Сообщение:</strong> ${escapeHtml(data.message || 'Задача успешно завершена')}</p>
        </div>
    `;

    return notification;
}

function setupEventHandlers() {
    const markAllReadBtn = document.getElementById('markAllReadBtn');
    const clearBtn = document.getElementById('clearBtn');

    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', () => {
            window.NotificationService.markAllAsRead();
            loadNotificationHistory();
            showMessage('Все уведомления отмечены как прочитанные');
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (confirm('Вы уверены, что хотите очистить все уведомления?')) {
                window.NotificationService.clearNotifications();
                loadNotificationHistory();
                showMessage('Все уведомления очищены');
            }
        });
    }
}

function limitNotifications(maxCount) {
    const notifications = document.querySelectorAll('.notification');
    if (notifications.length > maxCount) {
        for (let i = maxCount; i < notifications.length; i++) {
            notifications[i].remove();
        }
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showMessage(message) {
    console.log('Message:', message);
}