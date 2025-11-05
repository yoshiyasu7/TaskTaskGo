document.addEventListener('DOMContentLoaded', () => {
    if (!authManager.isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    const form = document.getElementById('editTaskForm');
    const titleEl = document.getElementById('title');
    const contentEl = document.getElementById('content');

    const match = location.pathname.match(/\/tasks\/(\d+)\/edit$/);
    const taskId = match ? Number(match[1]) : null;
    if (!taskId) {
        alert('Некорректный URL');
        return;
    }

    (async function loadTask() {
        const resp = await authManager.apiRequest('/api/v1/tasks/');
        const tasks = await resp.json();
        const task = Array.isArray(tasks) ? tasks.find(t => t.id === taskId) : null;
        if (task) {
            titleEl.value = task.title || '';
            contentEl.value = task.content || '';
        }
    })();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = { title: titleEl.value, content: contentEl.value };
        const resp = await authManager.apiRequest('/api/v1/tasks/' + taskId, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
        if (resp.ok) {
            window.location.href = '/profile';
        } else {
            alert('Не удалось обновить задачу');
        }
    });
});