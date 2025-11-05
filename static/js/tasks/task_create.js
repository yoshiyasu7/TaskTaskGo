document.addEventListener('DOMContentLoaded', () => {
    if (!authManager.isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    const params = new URLSearchParams(location.search);
    const presetProjectId = params.get('project_id');

    const form = document.getElementById('createTaskForm');
    const projectEl = document.getElementById('project');
    const titleEl = document.getElementById('title');
    const contentEl = document.getElementById('content');

    (async function loadProjects() {
        const resp = await authManager.apiRequest('/api/v1/projects/');
        const projects = await resp.json();
        if (!Array.isArray(projects) || projects.length === 0) {
            projectEl.innerHTML = '<option value="" disabled selected>Проекты не найдены</option>';
            projectEl.disabled = true;
            return;
        }
        projectEl.innerHTML = projects.map(p =>
            `<option value="${p.id}">${p.title}</option>`
        ).join('');

        if (presetProjectId) {
            projectEl.value = String(presetProjectId);
        }
    })();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            title: titleEl.value,
            content: contentEl.value,
            project_id: Number(projectEl.value)
        };
        const resp = await authManager.apiRequest('/api/v1/tasks/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        if (resp.ok) {
            window.location.href = '/profile';
        } else {
            alert('Не удалось создать задачу');
        }
    });
});