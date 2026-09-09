const API_BASE = 'http://localhost:3000/api';

function navigateTo(page) {
    window.location.href = '/' + page;
}

// 滑动消息条：替代 alert 弹窗
function showToast(message, type = 'info', duration = 2500) {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span class="toast-icon"></span><span class="toast-msg"></span>`;
    toast.querySelector('.toast-msg').textContent = message;

    container.appendChild(toast);

    // 触发进入动画
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // 自动滑出
    const timer = setTimeout(() => {
        closeToast(toast);
    }, duration);

    toast.addEventListener('click', () => {
        clearTimeout(timer);
        closeToast(toast);
    });
}

function closeToast(toast) {
    if (!toast) return;
    toast.classList.remove('show');
    toast.classList.add('leave');
    setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 350);
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
        const url = new URL(`${API_BASE}/spots/`);
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

async function loadFavoriteMap(spotIds) {
    const map = {};
    if (!getCurrentUser()) {
        return map;
    }

    const result = await fetchMyFavorites();
    if (!result || !Array.isArray(result.favorites)) {
        return map;
    }

    const wanted = new Set((spotIds || []).map(Number));
    for (const favorite of result.favorites) {
        if (wanted.size === 0 || wanted.has(Number(favorite.spot_id))) {
            map[favorite.spot_id] = true;
        }
    }
    return map;
}

/* ============ 旅游智能助手（右下角悬浮，仅旅游指南页面加载） ============ */
(function () {
    const MAX_HISTORY_TURNS = 6;
    let chatHistory = [];
    let isTyping = false;

    function initChatWidget() {
        // 仅在旅游指南页面（travel-tips.html）显示，其他页面不注入
        if (!/travel-tips\.html/i.test(window.location.pathname)) return;
        // 已存在则不重复注入
        if (document.getElementById('chatContainer')) return;

        const wrap = document.createElement('div');
        wrap.className = 'chat-container collapsed';
        wrap.id = 'chatContainer';
        wrap.innerHTML = `
            <div class="chat-header" id="chatHeader">
                <h4><span class="chat-icon">🤖</span> 智能旅游助手</h4>
                <span style="font-size: 20px;" id="chatToggleIcon">▼</span>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="chat-message bot">
                    <div class="chat-avatar">🤖</div>
                    <div class="chat-content">您好！我是您的四川旅游助手。关于四川旅游的任何问题都可以问我，比如最佳旅游时间、交通指南、旅游路线等。</div>
                </div>
            </div>
            <div class="chat-faq-tags">
                <span class="chat-faq-tag" data-q="最佳旅游时间">最佳旅游时间</span>
                <span class="chat-faq-tag" data-q="怎么去四川">交通指南</span>
                <span class="chat-faq-tag" data-q="推荐旅游路线">旅游路线</span>
                <span class="chat-faq-tag" data-q="高原反应">高原反应预防</span>
                <span class="chat-faq-tag" data-q="四川美食">四川美食</span>
                <span class="chat-faq-tag" data-q="注意事项">注意事项</span>
            </div>
            <div class="chat-input-area">
                <input type="text" class="chat-input" id="chatInput" placeholder="输入您的问题...">
                <button class="chat-send-btn" id="chatSendBtn">发送</button>
            </div>
        `;
        document.body.appendChild(wrap);

        const header = document.getElementById('chatHeader');
        const input = document.getElementById('chatInput');
        const sendBtn = document.getElementById('chatSendBtn');
        const icon = document.getElementById('chatToggleIcon');

        header.addEventListener('click', () => {
            wrap.classList.toggle('collapsed');
            icon.textContent = wrap.classList.contains('collapsed') ? '▼' : '▲';
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });

        sendBtn.addEventListener('click', () => sendMessage());

        wrap.querySelectorAll('.chat-faq-tag').forEach((tag) => {
            tag.addEventListener('click', () => {
                input.value = tag.dataset.q;
                sendMessage();
            });
        });
    }

    function addMessage(text, isUser) {
        const box = document.getElementById('chatMessages');
        const div = document.createElement('div');
        div.className = `chat-message ${isUser ? 'user' : 'bot'}`;
        if (!isUser) {
            const avatar = document.createElement('div');
            avatar.className = 'chat-avatar';
            avatar.textContent = '🤖';
            div.appendChild(avatar);
        }
        const content = document.createElement('div');
        content.className = 'chat-content';
        // 转义 HTML 防 XSS，再处理换行
        const escaped = String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>');
        content.innerHTML = escaped;
        div.appendChild(content);
        box.appendChild(div);
        box.scrollTop = box.scrollHeight;
    }

    function showTyping() {
        const box = document.getElementById('chatMessages');
        const div = document.createElement('div');
        div.className = 'chat-message bot';
        div.id = 'typingIndicator';
        div.innerHTML = `<div class="chat-avatar">🤖</div>
            <div class="chat-content"><div class="chat-typing"><span></span><span></span><span></span></div></div>`;
        box.appendChild(div);
        box.scrollTop = box.scrollHeight;
        isTyping = true;
    }

    function hideTyping() {
        const t = document.getElementById('typingIndicator');
        if (t) t.remove();
        isTyping = false;
    }

    function setLoading(loading) {
        const btn = document.getElementById('chatSendBtn');
        const input = document.getElementById('chatInput');
        if (btn) {
            btn.disabled = !!loading;
            btn.textContent = loading ? '回答中...' : '发送';
        }
        if (input) input.disabled = !!loading;
    }

    async function sendMessage() {
        const input = document.getElementById('chatInput');
        const question = input.value.trim();
        if (!question || isTyping) return; // 空问题 / 防重复提交

        input.value = '';
        setLoading(true);
        addMessage(question, true);
        chatHistory.push({ role: 'user', content: question });
        showTyping();

        try {
            const resp = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    history: chatHistory.slice(-MAX_HISTORY_TURNS * 2)
                })
            });
            const data = await resp.json();
            hideTyping();

            const answer = (data && (data.answer || data.response)) || '';
            if (data && data.success && answer) {
                addMessage(answer, false);
                chatHistory.push({ role: 'assistant', content: answer });
                while (chatHistory.length > MAX_HISTORY_TURNS * 2) chatHistory.shift();
            } else {
                addMessage((data && data.message) || '抱歉，我暂时无法回答这个问题，请稍后再试。', false);
                chatHistory.pop(); // 失败回滚，不污染历史
            }
        } catch (e) {
            hideTyping();
            addMessage('网络连接异常，请检查后端服务是否启动后重试。', false);
            chatHistory.pop();
        } finally {
            setLoading(false);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChatWidget);
    } else {
        initChatWidget();
    }
})();
