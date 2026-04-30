document.addEventListener('DOMContentLoaded', function() {
    // DOM元素
    const profileForm = document.getElementById('profile-form');
    const avatarDisplay = document.getElementById('avatar-display');
    const emojiSelectors = document.querySelectorAll('.emoji-selector');
    const tagInput = document.getElementById('tag-input');
    const tagsContainer = document.getElementById('tags-container');
    const previewBtn = document.getElementById('preview-btn');
    
    // 状态变量
    let selectedEmoji = '😊';
    let tags = [];
    
    // 从localStorage加载资料
    loadProfile();
    
    // 头像选择
    emojiSelectors.forEach(emoji => {
        emoji.addEventListener('click', function() {
            // 移除之前的选中状态
            emojiSelectors.forEach(e => e.classList.remove('selected'));
            
            // 添加选中状态
            this.classList.add('selected');
            selectedEmoji = this.dataset.emoji;
            avatarDisplay.textContent = selectedEmoji;
        });
    });
    
    // 滑块值更新
    document.getElementById('work-life-balance').addEventListener('input', function() {
        document.getElementById('work-life-value').textContent = this.value + '%';
    });
    
    document.getElementById('spending-habit').addEventListener('input', function() {
        document.getElementById('spending-value').textContent = this.value + '%';
    });
    
    document.getElementById('social-preference').addEventListener('input', function() {
        document.getElementById('social-value').textContent = this.value + '%';
    });
    
    // 标签输入
    tagInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && this.value.trim()) {
            e.preventDefault();
            addTag(this.value.trim());
            this.value = '';
        }
    });
    
    // 添加标签函数
    function addTag(tagText) {
        if (tags.includes(tagText)) {
            showNotification('标签已存在', 'warning');
            return;
        }
        
        if (tags.length >= 10) {
            showNotification('最多添加10个标签', 'warning');
            return;
        }
        
        tags.push(tagText);
        renderTags();
    }
    
    // 渲染标签
    function renderTags() {
        tagsContainer.innerHTML = '';
        tags.forEach((tag, index) => {
            const tagElement = document.createElement('span');
            tagElement.className = 'tag-input';
            tagElement.innerHTML = `
                ${tag}
                <span class="remove-tag" data-index="${index}">&times;</span>
            `;
            tagsContainer.appendChild(tagElement);
        });
        
        // 添加删除事件
        document.querySelectorAll('.remove-tag').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                tags.splice(index, 1);
                renderTags();
            });
        });
    }
    
    // 保存个人资料
    profileForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const profile = collectProfileData();
        
        // 验证必填项
        if (!profile.nickname) {
            showNotification('请输入昵称', 'warning');
            return;
        }
        
        // 保存到localStorage
        saveProfile(profile);
        
        showNotification('个人资料保存成功！', 'success');
        
        // 2秒后返回聊天室
        setTimeout(() => {
            window.location.href = '/bus-chat';
        }, 2000);
    });
    
    // 收集表单数据
    function collectProfileData() {
        // 收集价值观
        const values = [];
        document.querySelectorAll('#profile-form input[type="checkbox"][id^="value-"]:checked').forEach(cb => {
            values.push(cb.value);
        });
        
        // 收集话题
        const topics = [];
        document.querySelectorAll('#profile-form input[type="checkbox"][id^="topic-"]:checked').forEach(cb => {
            topics.push(cb.value);
        });
        
        const profile = {
            // 基本资料
            avatar: selectedEmoji,
            nickname: document.getElementById('nickname').value.trim(),
            age: document.getElementById('age').value,
            gender: document.getElementById('gender').value,
            city: document.getElementById('city').value.trim(),
            occupation: document.getElementById('occupation').value.trim(),
            bio: document.getElementById('bio').value.trim(),
            wechat: document.getElementById('wechat').value.trim(),
            
            // 兴趣爱好
            tags: tags,
            
            // 价值观与生活观（滑块值）
            workLifeBalance: parseInt(document.getElementById('work-life-balance').value),
            spendingHabit: parseInt(document.getElementById('spending-habit').value),
            socialPreference: parseInt(document.getElementById('social-preference').value),
            
            // 重要价值观
            values: values,
            
            // 生活方式
            sleepSchedule: document.getElementById('sleep-schedule').value,
            dietHabit: document.getElementById('diet-habit').value,
            exerciseFrequency: document.getElementById('exercise-frequency').value,
            learningGoal: document.getElementById('learning-goal').value.trim(),
            
            // 期望与目标
            expectation: document.getElementById('expectation').value.trim(),
            topics: topics,
            
            // 元数据
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        
        return profile;
    }
    
    // 保存到localStorage
    function saveProfile(profile) {
        try {
            localStorage.setItem('busChatProfile', JSON.stringify(profile));
            console.log('个人资料已保存:', profile);
        } catch (error) {
            console.error('保存失败:', error);
            showNotification('保存失败，请重试', 'danger');
        }
    }
    
    // 从localStorage加载
    function loadProfile() {
        try {
            const savedProfile = localStorage.getItem('busChatProfile');
            if (!savedProfile) {
                console.log('未找到保存的个人资料');
                return;
            }
            
            const profile = JSON.parse(savedProfile);
            console.log('加载个人资料:', profile);
            
            // 填充表单
            fillProfileForm(profile);
            
        } catch (error) {
            console.error('加载失败:', error);
        }
    }
    
    // 填充表单
    function fillProfileForm(profile) {
        // 头像
        if (profile.avatar) {
            selectedEmoji = profile.avatar;
            avatarDisplay.textContent = selectedEmoji;
            emojiSelectors.forEach(emoji => {
                if (emoji.dataset.emoji === selectedEmoji) {
                    emoji.classList.add('selected');
                }
            });
        }
        
        // 基本资料
        document.getElementById('nickname').value = profile.nickname || '';
        document.getElementById('age').value = profile.age || '';
        document.getElementById('gender').value = profile.gender || '';
        document.getElementById('city').value = profile.city || '';
        document.getElementById('occupation').value = profile.occupation || '';
        document.getElementById('bio').value = profile.bio || '';
        document.getElementById('wechat').value = profile.wechat || '';

        // 标签
        if (profile.tags && Array.isArray(profile.tags)) {
            tags = profile.tags;
            renderTags();
        }
        
        // 滑块值
        if (profile.workLifeBalance !== undefined) {
            document.getElementById('work-life-balance').value = profile.workLifeBalance;
            document.getElementById('work-life-value').textContent = profile.workLifeBalance + '%';
        }
        
        if (profile.spendingHabit !== undefined) {
            document.getElementById('spending-habit').value = profile.spendingHabit;
            document.getElementById('spending-value').textContent = profile.spendingHabit + '%';
        }
        
        if (profile.socialPreference !== undefined) {
            document.getElementById('social-preference').value = profile.socialPreference;
            document.getElementById('social-value').textContent = profile.socialPreference + '%';
        }
        
        // 价值观复选框
        if (profile.values && Array.isArray(profile.values)) {
            profile.values.forEach(value => {
                const checkbox = document.querySelector(`input[type="checkbox"][value="${value}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }
        
        // 生活方式
        document.getElementById('sleep-schedule').value = profile.sleepSchedule || '';
        document.getElementById('diet-habit').value = profile.dietHabit || '';
        document.getElementById('exercise-frequency').value = profile.exerciseFrequency || '';
        document.getElementById('learning-goal').value = profile.learningGoal || '';
        
        // 期望与目标
        document.getElementById('expectation').value = profile.expectation || '';
        
        // 话题复选框
        if (profile.topics && Array.isArray(profile.topics)) {
            profile.topics.forEach(topic => {
                const checkbox = document.querySelector(`input[type="checkbox"][value="${topic}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }
    }
    
    // 预览资料
    previewBtn.addEventListener('click', function() {
        const profile = collectProfileData();
        showProfilePreview(profile);
    });
    
    // 显示资料预览
    function showProfilePreview(profile) {
        const modalHtml = `
            <div class="modal fade" id="previewModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-gradient-primary text-white">
                            <h5 class="modal-title">
                                <i class="bi bi-eye me-2"></i>个人资料预览
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="text-center mb-4">
                                <div style="font-size: 80px;">${profile.avatar}</div>
                                <h3 class="mt-3">${profile.nickname || '未设置昵称'}</h3>
                                ${profile.bio ? `<p class="text-muted">${profile.bio}</p>` : ''}
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <h5 class="mb-3"><i class="bi bi-person-fill me-2"></i>基本信息</h5>
                                    <ul class="list-unstyled">
                                        ${profile.age ? `<li><strong>年龄：</strong>${profile.age}岁</li>` : ''}
                                        ${profile.gender ? `<li><strong>性别：</strong>${getGenderText(profile.gender)}</li>` : ''}
                                        ${profile.city ? `<li><strong>城市：</strong>${profile.city}</li>` : ''}
                                        ${profile.occupation ? `<li><strong>职业：</strong>${profile.occupation}</li>` : ''}
                                        ${profile.wechat ? `<li><strong>微信：</strong><span class="text-success">${profile.wechat}</span></li>` : ''}
                                    </ul>
                                </div>
                                
                                <div class="col-md-6">
                                    <h5 class="mb-3"><i class="bi bi-heart-fill me-2"></i>兴趣爱好</h5>
                                    ${profile.tags && profile.tags.length > 0 ? 
                                        `<div class="d-flex flex-wrap">${profile.tags.map(tag => `<span class="badge bg-primary me-1 mb-1">${tag}</span>`).join('')}</div>` : 
                                        '<p class="text-muted">未设置</p>'}
                                </div>
                            </div>
                            
                            <hr>
                            
                            <h5 class="mb-3"><i class="bi bi-lightbulb-fill me-2"></i>价值观与生活观</h5>
                            <div class="row">
                                <div class="col-md-4 mb-3">
                                    <small class="text-muted d-block">工作与生活平衡</small>
                                    <div class="progress" style="height: 8px;">
                                        <div class="progress-bar" style="width: ${profile.workLifeBalance}%"></div>
                                    </div>
                                    <small class="text-muted">${profile.workLifeBalance}% 生活优先</small>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <small class="text-muted d-block">消费观念</small>
                                    <div class="progress" style="height: 8px;">
                                        <div class="progress-bar bg-success" style="width: ${profile.spendingHabit}%"></div>
                                    </div>
                                    <small class="text-muted">${profile.spendingHabit}% 享受型</small>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <small class="text-muted d-block">社交偏好</small>
                                    <div class="progress" style="height: 8px;">
                                        <div class="progress-bar bg-info" style="width: ${profile.socialPreference}%"></div>
                                    </div>
                                    <small class="text-muted">${profile.socialPreference}% 外向</small>
                                </div>
                            </div>
                            
                            ${profile.values && profile.values.length > 0 ? `
                                <div class="mb-3">
                                    <strong>重要价值观：</strong>
                                    <div class="d-flex flex-wrap mt-2">
                                        ${profile.values.map(v => `<span class="badge bg-warning text-dark me-1 mb-1">${v}</span>`).join('')}
                                    </div>
                                </div>
                            ` : ''}
                            
                            <hr>
                            
                            <h5 class="mb-3"><i class="bi bi-house-heart-fill me-2"></i>生活方式</h5>
                            <ul class="list-unstyled">
                                ${profile.sleepSchedule ? `<li><strong>作息：</strong>${getSleepScheduleText(profile.sleepSchedule)}</li>` : ''}
                                ${profile.dietHabit ? `<li><strong>饮食：</strong>${getDietHabitText(profile.dietHabit)}</li>` : ''}
                                ${profile.exerciseFrequency ? `<li><strong>运动：</strong>${getExerciseText(profile.exerciseFrequency)}</li>` : ''}
                            </ul>
                            
                            ${profile.learningGoal ? `
                                <div class="mb-3">
                                    <strong>学习目标：</strong>
                                    <p class="mt-1">${profile.learningGoal}</p>
                                </div>
                            ` : ''}
                            
                            ${profile.expectation ? `
                                <div class="alert alert-info">
                                    <strong><i class="bi bi-star-fill me-2"></i>期望：</strong>
                                    ${profile.expectation}
                                </div>
                            ` : ''}
                            
                            ${profile.topics && profile.topics.length > 0 ? `
                                <div>
                                    <strong>想聊的话题：</strong>
                                    <div class="d-flex flex-wrap mt-2">
                                        ${profile.topics.map(t => `<span class="badge bg-secondary me-1 mb-1">${t}</span>`).join('')}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                            <button type="button" class="btn btn-primary" onclick="saveAndClose()">保存并关闭</button>
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
        const modal = new bootstrap.Modal(document.getElementById('previewModal'));
        modal.show();
        
        // 保存并关闭函数
        window.saveAndClose = function() {
            const profileData = collectProfileData();
            saveProfile(profileData);
            showNotification('个人资料保存成功！', 'success');
            modal.hide();
        };
    }
    
    // 辅助函数：获取文本描述
    function getGenderText(gender) {
        const map = {
            'male': '男',
            'female': '女',
            'other': '其他',
            'prefer-not-to-say': '保密'
        };
        return map[gender] || gender;
    }
    
    function getSleepScheduleText(schedule) {
        const map = {
            'early-bird': '早起鸟（6点前起床）',
            'normal': '正常作息（6-8点起床）',
            'night-owl': '夜猫子（8点后起床）',
            'irregular': '不规律'
        };
        return map[schedule] || schedule;
    }
    
    function getDietHabitText(habit) {
        const map = {
            'omnivore': '不挑食，什么都吃',
            'healthy': '健康饮食，少油少盐',
            'vegetarian': '素食主义者',
            'foodie': '美食爱好者，喜欢探索',
            'simple': '简单就好，不讲究'
        };
        return map[habit] || habit;
    }
    
    function getExerciseText(freq) {
        const map = {
            'daily': '每天运动',
            'often': '经常运动（每周3-5次）',
            'sometimes': '偶尔运动（每周1-2次）',
            'rarely': '很少运动',
            'never': '几乎不运动'
        };
        return map[freq] || freq;
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
});
