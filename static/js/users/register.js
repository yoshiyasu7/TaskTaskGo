document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
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
            const resp = await fetch('/api/v1/auth/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                errorEl.textContent = err.detail || 'Ошибка регистрации';
                errorEl.style.display = 'block';
                return;
            }

            window.location.href = '/login';
        } catch {
            errorEl.textContent = 'Ошибка соединения';
            errorEl.style.display = 'block';
        }
    });
});