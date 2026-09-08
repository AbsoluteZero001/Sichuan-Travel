const API_BASE = 'http://localhost:3000/api';

function navigateTo(page) {
    window.location.href = '/' + page;
}

function getCurrentUser() {
    return JSON.parse(localStorage.getItem('user') || 'null');
}

function getToken() {
    return localStorage.getItem('token') || '';
}

function setCurrentUser(user, token) {
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('token', token);
}

function logout() {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    window.location.href = '/';
}

function updateAuthLinks() {
    const authLinks = document.querySelector('.auth-links');
    if (!authLinks) return;

    const user = getCurrentUser();

    if (!user) {
        authLinks.innerHTML = `
            <a href="/login.html">登录</a>
            <a href="/register.html">注册</a>
        `;
    } else if (user.role === 'admin') {
        authLinks.innerHTML = `
            <span>${user.username}</span>
            <a href="/admin-panel.html">管理面板</a>
            <a href="#" onclick="logout()">退出</a>
        `;
    } else {
        authLinks.innerHTML = `
            <span>${user.username}</span>
            <a href="/user-profile.html">个人中心</a>
            <a href="#" onclick="logout()">退出</a>
        `;
    }
}

function getAuthHeaders() {
    const token = getToken();
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

async function fetchSpots(keyword = '', season = '') {
    try {
        const url = new URL(`${API_BASE}/spots`);
        if (keyword) url.searchParams.append('keyword', keyword);
        if (season) url.searchParams.append('season', season);
        
        const response = await fetch(url.toString());
        if (!response.ok) throw new Error('网络错误');
        const result = await response.json();
        
        if (result.success) {
            return { spots: result.data, total: result.data.length, page: 1, pages: 1 };
        } else {
            return { spots: [], total: 0, page: 1, pages: 1 };
        }
    } catch (error) {
        console.error('获取景点失败:', error);
        return { spots: [], total: 0, page: 1, pages: 1 };
    }
}

async function fetchSpotById(id) {
    try {
        const response = await fetch(`${API_BASE}/spots/${id}`);
        if (!response.ok) throw new Error('网络错误');
        const result = await response.json();
        
        if (result.success) {
            return result.data;
        } else {
            return null;
        }
    } catch (error) {
        console.error('获取景点详情失败:', error);
        return null;
    }
}

async function addSpot(spotData) {
    try {
        const response = await fetch(`${API_BASE}/spots`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(spotData),
        });
        if (!response.ok) throw new Error('网络错误');
        return await response.json();
    } catch (error) {
        console.error('添加景点失败:', error);
        return { success: false, message: '添加失败' };
    }
}

async function updateSpot(id, spotData) {
    try {
        const response = await fetch(`${API_BASE}/spots/${id}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(spotData),
        });
        if (!response.ok) throw new Error('网络错误');
        return await response.json();
    } catch (error) {
        console.error('更新景点失败:', error);
        return { success: false, message: '更新失败' };
    }
}

async function deleteSpot(id) {
    try {
        const response = await fetch(`${API_BASE}/spots/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders(),
        });
        const result = await response.json();
        return result.success;
    } catch (error) {
        console.error('删除景点失败:', error);
        return false;
    }
}

async function registerUser(userData) {
    try {
        const response = await fetch(`${API_BASE}/users/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData),
        });
        return await response.json();
    } catch (error) {
        console.error('注册失败:', error);
        return { success: false, message: '注册失败: ' + error.message };
    }
}

async function loginUser(userData) {
    try {
        const response = await fetch(`${API_BASE}/users/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData),
        });
        return await response.json();
    } catch (error) {
        console.error('登录失败:', error);
        return { success: false, message: '登录失败: ' + error.message };
    }
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function validatePhone(phone) {
    const regex = /^1[3-9]\d{9}$/;
    return regex.test(phone);
}

async function fetchSpotFavorite(spotId) {
    try {
        const url = new URL(`${API_BASE}/favorites/`);
        url.searchParams.append('spot_id', spotId);
        
        const response = await fetch(url.toString(), {
            headers: getAuthHeaders()
        });
        const result = await response.json();
        
        if (result.success) {
            return result.data;
        } else {
            return null;
        }
    } catch (error) {
        console.error('获取收藏信息失败:', error);
        return null;
    }
}

async function addFavorite(spotId) {
    try {
        const response = await fetch(`${API_BASE}/favorites/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ spot_id: spotId }),
        });
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('添加收藏失败:', error);
        return { success: false, message: '添加收藏失败: ' + error.message };
    }
}

async function fetchAllFavorites(keyword = '') {
    try {
        const url = new URL(`${API_BASE}/favorites/`);
        if (keyword) url.searchParams.append('keyword', keyword);
        
        const response = await fetch(url.toString(), {
            headers: getAuthHeaders()
        });
        const result = await response.json();
        
        if (result.success) {
            return { favorites: result.data };
        } else {
            return { favorites: [] };
        }
    } catch (error) {
        console.error('获取收藏失败:', error);
        return { favorites: [] };
    }
}

async function deleteFavorite(id) {
    try {
        const response = await fetch(`${API_BASE}/favorites/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders(),
        });
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('删除收藏失败:', error);
        return { success: false, message: '删除收藏失败' };
    }
}

async function removeFavoriteBySpot(spotId) {
    try {
        const response = await fetch(`${API_BASE}/favorites/remove/${spotId}`, {
            method: 'DELETE',
            headers: getAuthHeaders(),
        });
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('取消收藏失败:', error);
        return { success: false, message: '取消收藏失败' };
    }
}

async function fetchMyFavorites() {
    try {
        const response = await fetch(`${API_BASE}/users/my-favorites`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        const result = await response.json();
        
        if (result.success) {
            return { favorites: result.data };
        } else {
            return { favorites: [] };
        }
    } catch (error) {
        console.error('获取我的收藏失败:', error);
        return { favorites: [] };
    }
}