document.addEventListener('DOMContentLoaded', function() {
    // DOM元素
    const joinForm = document.getElementById('join-form');
    const chatRoom = document.getElementById('chat-room');
    const usernameForm = document.getElementById('username-form');
    const usernameInput = document.getElementById('username-input');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const leaveBtn = document.getElementById('leave-btn');
    
    // 状态变量
    let userId = null;
    let username = null;
    let chatStartTime = null;
    let messagePollingInterval = null;
    let busStatusInterval = null;
    let durationInterval = null;
    
    // 加入聊天室
    usernameForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        username = usernameInput.value.trim();
        if (!username) {
            showNotification('请输入昵称', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/chat/join', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username })
            });
            
            const data = await response.json();
            
            if (data.success) {
                userId = data.user_id;
                chatStartTime = data.chat_start_time;
                
                // 显示聊天室
                joinForm.classList.add('d-none');
                chatRoom.classList.remove('d-none');
                
                // 加载历史消息
                loadMessages(data.messages);
                
                // 开始轮询
                startPolling();
                
                // 更新在线人数
                updateOnlineCount(data.online_count);
                
                showNotification(`欢迎 ${username}！`, 'success');
            }
        } catch (error) {
            console.error('加入聊天室失败:', error);
            showNotification('加入失败，请重试', 'danger');
        }
    });
    
    // 发送消息
    messageForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message || !userId) return;
        
        try {
            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_id: userId, message })
            });
            
            const data = await response.json();
            
            if (data.success) {
                messageInput.value = '';
                // 立即获取最新消息
                await fetchMessages();
            }
        } catch (error) {
            console.error('发送消息失败:', error);
            showNotification('发送失败', 'danger');
        }
    });
    
    // 离开聊天室
    leaveBtn.addEventListener('click', async function() {
        if (confirm('确定要离开聊天室吗？')) {
            await leaveChat();
        }
    });
    
    // 离开聊天室函数
    async function leaveChat() {
        if (userId) {
            try {
                await fetch('/api/chat/leave', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ user_id: userId })
                });
            } catch (error) {
                console.error('离开聊天室失败:', error);
            }
        }
        
        // 停止轮询
        stopPolling();
        
        // 返回加入页面
        chatRoom.classList.add('d-none');
        joinForm.classList.remove('d-none');
        usernameInput.value = '';
        userId = null;
        username = null;
        
        showNotification('已离开聊天室', 'info');
    }
    
    // 开始轮询
    function startPolling() {
        // 每2秒获取一次消息
        messagePollingInterval = setInterval(fetchMessages, 2000);
        
        // 每5秒更新一次公交车状态
        busStatusInterval = setInterval(updateBusStatus, 5000);
        
        // 每秒更新聊天时长
        durationInterval = setInterval(updateDuration, 1000);
        
        // 立即执行一次
        updateBusStatus();
    }
    
    // 停止轮询
    function stopPolling() {
        if (messagePollingInterval) {
            clearInterval(messagePollingInterval);
        }
        if (busStatusInterval) {
            clearInterval(busStatusInterval);
        }
        if (durationInterval) {
            clearInterval(durationInterval);
        }
    }
    
    // 获取消息
    async function fetchMessages() {
        if (!userId) return;
        
        try {
            const response = await fetch(`/api/chat/messages?user_id=${userId}`);
            const data = await response.json();
            
            loadMessages(data.messages);
            updateOnlineCount(data.online_count);
            updateDurationDisplay(data.chat_duration);
            
            // 检查是否可以加好友
            if (data.can_add_friend) {
                document.getElementById('friend-badge').classList.remove('d-none');
            }
        } catch (error) {
            console.error('获取消息失败:', error);
        }
    }
    
    // 加载消息
    function loadMessages(messages) {
        if (!messages || messages.length === 0) {
            chatMessages.innerHTML = `
                <div class="text-center py-5 text-muted">
                    <i class="bi bi-chat-square-text display-1 opacity-25"></i>
                    <p class="mt-3">等待第一条消息...</p>
                </div>
            `;
            return;
        }
        
        chatMessages.innerHTML = '';
        
        messages.forEach(msg => {
            const messageEl = createMessageElement(msg);
            chatMessages.appendChild(messageEl);
        });
        
        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 更新消息计数
        document.getElementById('message-count').textContent = `${messages.length} 条消息`;
    }
    
    // 创建消息元素
    function createMessageElement(msg) {
        const div = document.createElement('div');
        div.className = 'message-item';
        
        if (msg.type === 'system') {
            // 系统消息
            div.innerHTML = `
                <div class="message-bubble system">
                    <i class="bi bi-info-circle me-1"></i>
                    ${msg.message}
                    ${msg.online_count ? `<span class="ms-2">(${msg.online_count}人在线)</span>` : ''}
                </div>
            `;
        } else {
            // 普通消息
            const isOwn = msg.user_id === userId;
            const time = new Date(msg.timestamp * 1000).toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            div.innerHTML = `
                <div class="message-bubble ${isOwn ? 'own' : 'other'}">
                    ${!isOwn ? `<div class="message-header">${msg.username}</div>` : ''}
                    <div>${escapeHtml(msg.message)}</div>
                    <div class="message-time">${time}</div>
                </div>
            `;
        }
        
        return div;
    }
    
    // 更新在线人数
    function updateOnlineCount(count) {
        document.getElementById('online-count').textContent = count;
        document.getElementById('chat-online-count').textContent = count;
    }
    
    // 更新聊天时长
    function updateDuration() {
        if (chatStartTime) {
            const duration = Math.floor(Date.now() / 1000 - chatStartTime);
            updateDurationDisplay(duration);
        }
    }
    
    function updateDurationDisplay(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        const timeStr = `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        document.getElementById('chat-duration').textContent = timeStr;
    }
    
    // 更新公交车状态
    async function updateBusStatus() {
        try {
            const response = await fetch('/api/chat/bus-status');
            const data = await response.json();
            
            // 更新倒计时
            const countdown = data.next_bus_in;
            document.getElementById('bus-countdown').textContent = countdown.toFixed(1);
            document.getElementById('bus-countdown-small').textContent = countdown.toFixed(1);
            
            // 更新文本
            if (countdown <= 0.5) {
                document.getElementById('bus-time-text').textContent = '即将到站！';
            } else {
                document.getElementById('bus-time-text').textContent = `预计 ${countdown.toFixed(1)} 分钟后到站`;
            }
            
            // 显示延误信息
            const delayAlert = document.getElementById('bus-delay-alert');
            const delayInfo = document.getElementById('bus-delay-info');
            
            if (data.is_delayed && data.delay_reason) {
                document.getElementById('delay-reason').textContent = `延误提示：${data.delay_reason}`;
                document.getElementById('bus-delay-text').textContent = data.delay_reason;
                delayAlert.classList.remove('d-none');
                delayInfo.classList.remove('d-none');
            } else {
                delayAlert.classList.add('d-none');
                delayInfo.classList.add('d-none');
            }
            
            // 如果没有人在线，显示提示
            if (data.online_users === 0) {
                showEmptyState();
            }
        } catch (error) {
            console.error('获取公交状态失败:', error);
        }
    }
    
    // 显示空状态提示
    function showEmptyState() {
        const emptyMsg = document.createElement('div');
        emptyMsg.className = 'message-item';
        emptyMsg.innerHTML = `
            <div class="message-bubble system">
                <i class="bi bi-emoji-frown me-1"></i>
                当前还没有其他人在线，耐心等待或稍后再来吧~
            </div>
        `;
        
        // 检查是否已经有这条消息
        const existingMessages = chatMessages.querySelectorAll('.message-bubble.system');
        const hasEmptyMsg = Array.from(existingMessages).some(el => 
            el.textContent.includes('当前还没有其他人在线')
        );
        
        if (!hasEmptyMsg) {
            chatMessages.appendChild(emptyMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    // HTML转义
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // 显示通知
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; animation: slideInRight 0.3s ease;';
        notification.innerHTML = `
            <i class="bi bi-${getNotificationIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
    
    function getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'danger': 'x-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    // 添加CSS动画
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    // 页面关闭时自动离开
    window.addEventListener('beforeunload', function() {
        if (userId) {
            navigator.sendBeacon('/api/chat/leave', JSON.stringify({ user_id: userId }));
        }
    });
});
