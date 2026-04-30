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
                
                // 检查是否有保存的个人资料
                checkSavedProfile();
            }
        } catch (error) {
            console.error('加入聊天室失败:', error);
            showNotification('加入失败，请重试', 'danger');
        }
    });
    
    // 检查是否有保存的个人资料
    function checkSavedProfile() {
        try {
            const savedProfile = localStorage.getItem('busChatProfile');
            if (savedProfile) {
                const profile = JSON.parse(savedProfile);
                if (profile.nickname && profile.nickname !== username) {
                    // 如果资料中的昵称与当前不同，提示用户
                    showNotification(`检测到已保存的资料 "${profile.nickname}"，点击"我的资料"查看`, 'info');
                }
            }
        } catch (error) {
            console.error('检查个人资料失败:', error);
        }
    }

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

        // 为查看资料按钮添加事件监听
        attachViewProfileListeners();
    }

    // 附加查看资料按钮的事件监听器
    function attachViewProfileListeners() {
        const buttons = chatMessages.querySelectorAll('.view-profile-btn');
        buttons.forEach(btn => {
            // 移除旧的事件监听器以防重复绑定（虽然innerHTML重置后通常不需要，但这是好习惯）
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            
            newBtn.addEventListener('click', function() {
                const targetUserId = this.dataset.userId;
                const targetUsername = this.dataset.username;
                viewUserProfile(targetUserId, targetUsername);
            });
        });
    }

    // 获取聊天时长（秒）
    function getChatDuration() {
        if (!chatStartTime) return 0;
        return Math.floor(Date.now() / 1000 - chatStartTime);
    }

    // 查看用户资料
    function viewUserProfile(targetUserId, targetUsername) {
        // 检查是否聊天满5分钟
        const chatDuration = getChatDuration();
        
        if (chatDuration < 300) { // 300秒 = 5分钟
            const remainingTime = 300 - chatDuration;
            const minutes = Math.floor(remainingTime / 60);
            const seconds = remainingTime % 60;
            
            showNotification(
                `还需聊天 ${minutes}分${seconds}秒 才能查看资料`, 
                'warning'
            );
            return;
        }
        
        // 尝试从localStorage获取自己的资料（作为示例）
        // 在实际应用中，这里应该从服务器获取对方的资料
        try {
            const myProfile = localStorage.getItem('busChatProfile');
            
            if (!myProfile) {
                showNotification('您还没有完善个人资料，先去完善一下吧！', 'info');
                setTimeout(() => {
                    window.location.href = '/profile';
                }, 2000);
                return;
            }
            
            // 显示模拟的对方资料（实际应该从服务器获取）
            showOtherUserProfile(targetUserId, targetUsername);
            
        } catch (error) {
            console.error('查看资料失败:', error);
            showNotification('查看资料失败，请重试', 'danger');
        }
    }

    // 显示对方资料（模拟）
    function showOtherUserProfile(userId, username) {
        // 在实际应用中，这里应该通过API获取对方的真实资料
        // 由于我们使用localStorage，每个用户只能访问自己的资料
        // 这里展示一个模拟的交互
        
        const modalHtml = `
            <div class="modal fade" id="userProfileModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-gradient-primary text-white">
                            <h5 class="modal-title">
                                <i class="bi bi-person-badge-fill me-2"></i>
                                ${escapeHtml(username)} 的个人资料
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-success">
                                <i class="bi bi-check-circle-fill me-2"></i>
                                <strong>恭喜！</strong>你们已经聊天超过5分钟，可以互相查看资料了。
                            </div>
                            
                            <div class="text-center mb-4">
                                <div style="font-size: 80px;">👤</div>
                                <h3 class="mt-3">${escapeHtml(username)}</h3>
                                <p class="text-muted">等公交聊天室用户</p>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <h5 class="mb-3"><i class="bi bi-person-fill me-2"></i>基本信息</h5>
                                    <ul class="list-unstyled">
                                        <li><strong>昵称：</strong>${escapeHtml(username)}</li>
                                        <li><strong>用户ID：</strong><small class="text-muted">${userId}</small></li>
                                    </ul>
                                </div>
                                
                                <div class="col-md-6">
                                    <h5 class="mb-3"><i class="bi bi-wechat me-2 text-success"></i>联系方式</h5>
                                    <div class="alert alert-info">
                                        <p class="mb-2"><strong>提示：</strong></p>
                                        <p class="mb-0 small">
                                            对方需要在其个人资料中设置微信号后，您才能看到。<br>
                                            建议您也去完善个人资料，方便他人联系您。
                                        </p>
                                    </div>
                                </div>
                            </div>
                            
                            <hr>
                            
                            <div class="text-center">
                                <a href="/profile" class="btn btn-primary rounded-pill">
                                    <i class="bi bi-pencil-square me-2"></i>完善我的资料
                                </a>
                            </div>
                            
                            <div class="mt-3 text-center">
                                <small class="text-muted">
                                    <i class="bi bi-shield-check me-1"></i>
                                    保护隐私，仅在聊天满5分钟后可见
                                </small>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                            <button type="button" class="btn btn-success" onclick="copyContactInfo()">
                                <i class="bi bi-clipboard me-2"></i>复制联系方式
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 添加模态框到页面
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = modalHtml;
        document.body.appendChild(tempDiv.firstElementChild);
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('userProfileModal'));
        modal.show();
        
        // 复制联系方式函数
        window.copyContactInfo = function() {
            showNotification('请先让对方完善资料中的微信号', 'info');
        };
        
        // 模态框关闭时清理
        document.getElementById('userProfileModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
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
                    ${!isOwn ? `
                        <div class="message-header d-flex justify-content-between align-items-center">
                            <span>${escapeHtml(msg.username)}</span>
                            <button class="btn btn-sm btn-outline-light view-profile-btn" 
                                    data-user-id="${msg.user_id}" 
                                    data-username="${escapeHtml(msg.username)}"
                                    title="查看资料">
                                <i class="bi bi-person-badge"></i>
                            </button>
                        </div>
                    ` : '<div class="message-header"></div>'}
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
