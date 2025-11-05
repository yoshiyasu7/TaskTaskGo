document.addEventListener('DOMContentLoaded', () => {
    if (!authManager.isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    const btn = document.getElementById('confirm');
    const match = location.pathname.match(/\/projects\/(\d+)\/delete$/);
    const projectId = match ? Number(match[1]) : null;
    if (!projectId) {
        alert('Некорректный URL');
        return;
    }

    btn.addEventListener('click', async () => {
        const resp = await authManager.apiRequest('/api/v1/projects/' + projectId, { method: 'POST' });
        if (resp.ok) {
            window.location.href = '/profile';
        } else {
            alert('Не удалось удалить проект');
        }
    });
});