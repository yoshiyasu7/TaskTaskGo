/**
 * Система управления JWT токенами для TaskTaskGo
 */
class AuthManager {
    constructor() {
        this.tokenKey = 'tasktaskgo_jwt_token';
        this.refreshTokenKey = 'tasktaskgo_refresh_token';
        this.apiBaseUrl = window.location.origin;
        this.setupAxiosInterceptors();
    }

    saveToken(token, refreshToken = null) {
        localStorage.setItem(this.tokenKey, token);
        if (refreshToken) {
            localStorage.setItem(this.refreshTokenKey, refreshToken);
        }
    }

    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    removeToken() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.refreshTokenKey);
    }

    isAuthenticated() {
        const token = this.getToken();
        if (!token) return false;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const currentTime = Math.floor(Date.now() / 1000);
            return payload.exp > currentTime;
        } catch {
            this.removeToken();
            return false;
        }
    }

    getAuthHeaders() {
        const token = this.getToken();
        return token ? {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        } : {
            'Content-Type': 'application/json'
        };
    }

    async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: this.getAuthHeaders(),
            credentials: 'include'
        };
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: { ...defaultOptions.headers, ...options.headers }
        };
        const response = await fetch(url, mergedOptions);
        if (response.status === 401) {
            this.handleUnauthorized();
            throw new Error('Не авторизован');
        }
        return response;
    }

    handleUnauthorized() {
        this.removeToken();
        window.location.href = '/login';
    }

    setupAxiosInterceptors() {
        if (typeof axios !== 'undefined') {
            axios.interceptors.request.use(
                (config) => {
                    const token = this.getToken();
                    if (token) config.headers.Authorization = `Bearer ${token}`;
                    return config;
                },
                (error) => Promise.reject(error)
            );
            axios.interceptors.response.use(
                (response) => response,
                (error) => {
                    if (error.response?.status === 401) this.handleUnauthorized();
                    return Promise.reject(error);
                }
            );
        }
    }

    autoAuth() {
        if (this.isAuthenticated()) {
            this.loadUserData().catch(() => {});
        }
    }

    async loadUserData() {
        const response = await this.apiRequest('/api/v1/auth/user/');
        return await response.json();
    }
}

const authManager = new AuthManager();

document.addEventListener('DOMContentLoaded', () => {
    authManager.autoAuth();
});