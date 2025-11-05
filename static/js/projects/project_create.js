document.addEventListener('DOMContentLoaded', () => {
    if (!authManager.isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    const form = document.getElementById('createProjectForm');
    const titleEl = document.getElementById('title');
    const contentEl = document.getElementById('content');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = { title: titleEl.value, content: contentEl.value };
        const resp = await authManager.apiRequest('/api/v1/projects/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        if (resp.ok) {
            window.location.href = '/profile';
        } else {
            alert('Не удалось создать проект');
        }
    });
});