document.addEventListener('DOMContentLoaded', () => {
    if (!authManager.isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    const userInfoEl = document.getElementById('user-info');
    const projectsEl = document.getElementById('projects');
    const logoutBtn = document.getElementById('logout-btn');

    logoutBtn?.addEventListener('click', () => {
        authManager.removeToken();
        window.location.href = '/login';
    });

    (async function loadProfile() {
        try {
            const userResp = await authManager.apiRequest('/api/v1/auth/user/');
            const user = await userResp.json();
            userInfoEl.innerHTML = `
                <p><b>ID:</b> ${user.id}</p>
                <p><b>Имя:</b> ${user.username || ''}</p>
            `;

            const [projResp, tasksResp] = await Promise.all([
                authManager.apiRequest('/api/v1/projects/'),
                authManager.apiRequest('/api/v1/tasks/')
            ]);

            const projects = await projResp.json();
            const allTasks = await tasksResp.json();

            projectsEl.innerHTML = '';

            const addProjectDiv = document.createElement('div');
            addProjectDiv.className = 'actions';
            addProjectDiv.innerHTML = `<a href="/projects/create">Создать проект</a>`;
            projectsEl.appendChild(addProjectDiv);

            // Проверяем, есть ли проекты для отображения
            const hasProjects = Array.isArray(projects) && projects.length > 0;

            if (!hasProjects) {
                // Если проектов нет, показываем сообщение и завершаем выполнение
                const noProjectsMessage = document.createElement('div');
                noProjectsMessage.className = 'no-projects-message';
                noProjectsMessage.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #666;">
                        <p style="font-size: 18px; margin-bottom: 20px;">У вас пока нет проектов</p>
                        <p>Создайте первый проект, чтобы начать работу с задачами</p>
                    </div>
                `;
                projectsEl.appendChild(noProjectsMessage);
                return; // Прерываем выполнение, не доходя до основных кнопок
            }

            // Если проекты есть, продолжаем с группировкой задач
            const tasksByProject = new Map();
            if (Array.isArray(allTasks)) {
                for (const t of allTasks) {
                    const list = tasksByProject.get(t.project_id) || [];
                    list.push(t);
                    tasksByProject.set(t.project_id, list);
                }
            }

            // Отображаем проекты
            for (const project of projects) {
                const tasks = tasksByProject.get(project.id) || [];

                const div = document.createElement('div');
                div.className = 'project';
                div.innerHTML = `
                    <h3>${project.title}</h3>
                    <p>${project.content || ''}</p>
                    <div class="actions">
                        <a href="/projects/${project.id}/edit">Редактировать</a>
                        <a href="/projects/${project.id}/delete">Удалить</a>
                        <a href="/tasks/create?project_id=${project.id}">Создать задачу</a>
                    </div>
                    <div class="tasks">
                        <h4>Задачи</h4>
                        ${tasks.length > 0 ?
                            tasks.map(t => `
                                <div class="task">
                                    <div><b>${t.title}</b></div>
                                    <div>${t.content || ''}</div>
                                    <div class="actions">
                                        <a href="/tasks/${t.id}/edit">Редактировать</a>
                                        <a href="/tasks/${t.id}/delete">Удалить</a>
                                    </div>
                                </div>
                            `).join('') :
                            '<p>В этом проекте пока нет задач</p>'
                        }
                    </div>
                `;
                projectsEl.appendChild(div);
            }

        } catch (e) {
            console.error('Ошибка профиля:', e);

            // Обработка ошибок с показом сообщения
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.innerHTML = `
                <div style="background: #ffebee; border: 1px solid #f44336; border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <strong style="color: #c62828;">Ошибка загрузки:</strong>
                    <p style="margin: 5px 0 0 0; color: #333;">Не удалось загрузить данные. Пожалуйста, попробуйте позже.</p>
                    <button onclick="location.reload()" class="btn btn-primary" style="margin-top: 10px;">Обновить страницу</button>
                </div>
            `;
            projectsEl.appendChild(errorDiv);
        }
    })();
});