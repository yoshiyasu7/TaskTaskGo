document.addEventListener('DOMContentLoaded', () => {
    if (!authManager.isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    const btn = document.getElementById('confirm');
    const match = location.pathname.match(/\/tasks\/(\d+)\/delete$/);
    const taskId = match ? Number(match[1]) : null;
    if (!taskId) {
        alert('Некорректный URL');
        return;
    }

    btn.addEventListener('click', async () => {
        const resp = await authManager.apiRequest('/api/v1/tasks/' + taskId, { method: 'POST' });
        if (resp.ok) {
            window.location.href = '/profile';
        } else {
            alert('Не удалось удалить задачу');
        }
    });
});