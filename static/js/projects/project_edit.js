document.addEventListener('DOMContentLoaded', () => {
    if (!authManager.isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    const form = document.getElementById('editProjectForm');
    const titleEl = document.getElementById('title');
    const contentEl = document.getElementById('content');

    const match = location.pathname.match(/\/projects\/(\d+)\/edit$/);
    const projectId = match ? Number(match[1]) : null;
    if (!projectId) {
        alert('Некорректный URL');
        return;
    }

    (async function loadProject() {
        const resp = await authManager.apiRequest('/api/v1/projects/' + projectId);
        const list = await resp.json();
        const project = Array.isArray(list) ? list.find(p => p.id === projectId) : null;
        if (project) {
            titleEl.value = project.title || '';
            contentEl.value = project.content || '';
        }
    })();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = { title: titleEl.value, content: contentEl.value };
        const resp = await authManager.apiRequest('/api/v1/projects/' + projectId, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
        if (resp.ok) {
            window.location.href = '/profile';
        } else {
            alert('Не удалось обновить проект');
        }
    });
});