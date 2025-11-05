document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    const errorEl = document.getElementById('error-message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorEl.style.display = 'none';

        const formData = new FormData(form);
        const payload = {
            username: formData.get('username'),
            password: formData.get('password')
        };

        try {
            const resp = await fetch('/api/v1/auth/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                errorEl.textContent = err.detail || 'Неверные учетные данные';
                errorEl.style.display = 'block';
                return;
            }

            const data = await resp.json();
            authManager.saveToken(data.access_token);
            window.location.href = '/profile';
        } catch {
            errorEl.textContent = 'Ошибка соединения';
            errorEl.style.display = 'block';
        }
    });
});