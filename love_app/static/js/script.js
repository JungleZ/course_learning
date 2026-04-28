document.addEventListener('DOMContentLoaded', function() {
    const quoteText = document.getElementById('quote-text');
    const quoteCategory = document.getElementById('quote-category');
    const refreshBtn = document.getElementById('refresh-btn');
    const autoRefreshToggle = document.getElementById('auto-refresh');
    const countdownElement = document.getElementById('countdown');
    const totalQuotesElement = document.getElementById('total-quotes');
    
    let countdown = 5;
    let countdownInterval;
    let autoRefreshEnabled = true;
    
    // 语录分类映射 - 扩展版
    const categoryMap = {
        '基础恋爱观': ['爱不是占有', '真正的亲密关系', '健康的关系', '宽恕是爱情', '真爱的标志', '在爱情中，保持独立', '感恩是维持', '爱不是寻找', '爱需要持续', '小事的积累'],
        '情商与情绪': ['情商高的人懂得倾听', '脆弱不是弱点', '情商包括认识到', '沟通不是为了赢得', '情商高的人知道何时', '关系中的冲突', '自我爱是建立', '倾听比提供', '情商包括在压力', '学会识别并表达', '情绪稳定不是'],
        '沟通技巧': ['用我感受到代替', '有效的沟通始于', '不要在愤怒时', '说话前先思考', '沉默有时比言语', '表达需求时', '道歉不是示弱', '赞美要具体', '学会说不', '真正的沟通是心'],
        '相处之道': ['给彼此空间', '记住重要的日子', '一起做饭比', '不要试图改变', '定期约会', '分享彼此的梦想', '学会妥协', '在争吵后主动', '培养共同的兴趣', '遇到困难时', '每天至少一次', '学会欣赏对方'],
        '信任与忠诚': ['信任如同镜子', '诚实是爱情', '给对方查看手机', '忠诚不仅是身体', '疑心病是感情', '透明的沟通'],
        '成长与支持': ['最好的爱情是让', '支持对方的事业', '共同成长比', '鼓励对方追求', '在对方低谷时', '一起学习新事物'],
        '处理冲突': ['争吵时对事不对人', '冷静期不是冷战', '承认错误不可耻', '找到问题的根源', '学会换位思考', '不要在第三者面前', '设定吵架规则'],
        '亲密与浪漫': ['浪漫不需要昂贵', '身体接触是爱', '制造惊喜', '写一封手写信', '回忆初次相遇', '偶尔的小别胜新婚'],
        '长期关系': ['爱情需要经营', '定期回顾关系', '不要把对方的付出', '保持好奇心', '共同制定未来', '学会在平淡中', '经济独立是感情', '处理好与原生家庭'],
        '自我提升': ['先爱自己', '保持个人成长', '有自己的社交圈', '培养独立的兴趣', '身心健康是对', '学会独处'],
        '智慧金句': ['爱情不是1+1', '真正爱你的人', '合适的两个人', '爱情最美的样子', '好的感情', '爱对了人'],
        '异地恋': ['异地恋考验的不是距离', '视频通话不能替代', '为下次见面制定', '分享日常生活的小事', '异地恋需要更多的沟通', '把分离的时间当作', '定期的见面计划', '不要因为距离而降低'],
        '婚姻家庭': ['婚姻不是爱情的终点', '家务分工要公平', '在孩子面前展现', '婆媳关系的核心', '财务透明是婚姻', '记住结婚纪念日', '给彼此独处的时间', '共同承担育儿责任'],
        '分手疗愈': ['分手不是失败', '允许自己悲伤', '删除联系方式不是', '从每段关系中学习', '时间是最好的疗伤药', '不要因为害怕受伤', '结束一段关系前', '单身不是惩罚'],
        '约会初识': ['第一次约会', '观察对方如何对待', '不要太快投入', '共同的价值观比', '注意对方的言行', '约会时放下手机', '不要为了迎合对方', '第一印象很重要'],
        '边界尊重': ['健康的边界不是', '学会拒绝不合理', '尊重对方的隐私', '每个人都有自己的底线', '边界清晰的关系', '不要以爱的名义']
    };
    
    // 根据语录内容判断分类
    function detectCategory(quote) {
        for (const [category, keywords] of Object.entries(categoryMap)) {
            for (const keyword of keywords) {
                if (quote.includes(keyword)) {
                    return category;
                }
            }
        }
        return '情感智慧'; // 默认分类
    }
    
    // 获取分类图标
    function getCategoryIcon(category) {
        const iconMap = {
            '基础恋爱观': 'bi-heart',
            '情商与情绪': 'bi-emoji-smile',
            '沟通技巧': 'bi-chat-dots',
            '相处之道': 'bi-people',
            '信任与忠诚': 'bi-shield-check',
            '成长与支持': 'bi-graph-up',
            '处理冲突': 'bi-tools',
            '亲密与浪漫': 'bi-stars',
            '长期关系': 'bi-calendar-heart',
            '自我提升': 'bi-person-check',
            '智慧金句': 'bi-lightbulb',
            '异地恋': 'bi-geo-alt',
            '婚姻家庭': 'bi-house-heart',
            '分手疗愈': 'bi-bandaid',
            '约会初识': 'bi-cup-hot',
            '边界尊重': 'bi-shield-lock',
            '情感智慧': 'bi-brain'
        };
        return iconMap[category] || 'bi-quote';
    }
    
    // Function to fetch a new quote
    function fetchQuote() {
        // 显示加载状态
        quoteText.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>正在加载智慧语录...';
        quoteCategory.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>识别分类...';
        
        fetch('/api/quote')
            .then(response => response.json())
            .then(data => {
                // 检测分类
                const category = detectCategory(data.quote);
                const categoryIcon = getCategoryIcon(category);
                
                // 更新总数
                if (data.total_quotes) {
                    totalQuotesElement.textContent = data.total_quotes + '+';
                }
                
                // 淡出效果
                quoteText.style.opacity = '0';
                quoteText.style.transform = 'translateY(-10px)';
                quoteCategory.style.opacity = '0';
                
                setTimeout(() => {
                    // 更新语录文本
                    quoteText.textContent = data.quote;
                    
                    // 更新分类标签
                    quoteCategory.innerHTML = `<i class="bi ${categoryIcon} me-1"></i>${category}`;
                    
                    // 根据分类改变徽章颜色
                    updateCategoryBadgeColor(category);
                    
                    // 淡入效果
                    quoteText.style.opacity = '1';
                    quoteText.style.transform = 'translateY(0)';
                    quoteCategory.style.opacity = '1';
                }, 200);
                
                // 重置倒计时
                resetCountdown();
            })
            .catch(error => {
                console.error('Error fetching quote:', error);
                quoteText.innerHTML = '<i class="bi bi-exclamation-triangle text-warning me-2"></i>抱歉，加载失败。请稍后重试。';
                quoteCategory.innerHTML = '<i class="bi bi-x-circle me-1"></i>加载失败';
            });
    }
    
    // 根据分类更新徽章颜色
    function updateCategoryBadgeColor(category) {
        const colorMap = {
            '基础恋爱观': 'bg-danger',
            '情商与情绪': 'bg-success',
            '沟通技巧': 'bg-info',
            '相处之道': 'bg-primary',
            '信任与忠诚': 'bg-warning',
            '成长与支持': 'bg-success',
            '处理冲突': 'bg-secondary',
            '亲密与浪漫': 'bg-danger',
            '长期关系': 'bg-primary',
            '自我提升': 'bg-info',
            '智慧金句': 'bg-warning',
            '异地恋': 'bg-info',
            '婚姻家庭': 'bg-success',
            '分手疗愈': 'bg-secondary',
            '约会初识': 'bg-danger',
            '边界尊重': 'bg-warning',
            '情感智慧': 'bg-secondary'
        };
        
        // 移除所有颜色类
        quoteCategory.className = 'badge rounded-pill px-3 py-2';
        // 添加新的颜色类
        quoteCategory.classList.add(colorMap[category] || 'bg-primary');
    }
    
    // 倒计时功能
    function startCountdown() {
        clearInterval(countdownInterval);
        countdown = 5;
        countdownElement.textContent = countdown;
        
        countdownInterval = setInterval(() => {
            countdown--;
            countdownElement.textContent = countdown;
            
            if (countdown <= 0) {
                if (autoRefreshEnabled) {
                    fetchQuote();
                }
                countdown = 5;
            }
        }, 1000);
    }
    
    // 重置倒计时
    function resetCountdown() {
        countdown = 5;
        countdownElement.textContent = countdown;
    }
    
    // 手动刷新按钮
    refreshBtn.addEventListener('click', function() {
        // 添加按钮点击动画
        this.classList.add('active');
        setTimeout(() => {
            this.classList.remove('active');
        }, 200);
        
        fetchQuote();
    });
    
    // 自动刷新开关
    autoRefreshToggle.addEventListener('change', function() {
        autoRefreshEnabled = this.checked;
        
        if (autoRefreshEnabled) {
            startCountdown();
            // 显示提示
            showNotification('自动刷新已开启', 'success');
        } else {
            clearInterval(countdownInterval);
            countdownElement.textContent = '∞';
            // 显示提示
            showNotification('自动刷新已关闭', 'info');
        }
    });
    
    // 显示通知
    function showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; animation: slideInRight 0.3s ease;';
        notification.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // 3秒后自动消失
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
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
    
    // 收藏功能（示例）
    document.querySelector('.bi-bookmark').parentElement.addEventListener('click', function(e) {
        e.preventDefault();
        const icon = this.querySelector('i');
        if (icon.classList.contains('bi-bookmark')) {
            icon.classList.remove('bi-bookmark');
            icon.classList.add('bi-bookmark-fill');
            showNotification('已添加到收藏', 'success');
        } else {
            icon.classList.remove('bi-bookmark-fill');
            icon.classList.add('bi-bookmark');
            showNotification('已取消收藏', 'info');
        }
    });
    
    // 喜欢功能（示例）
    document.querySelector('.bi-heart').parentElement.addEventListener('click', function(e) {
        e.preventDefault();
        const icon = this.querySelector('i');
        if (icon.classList.contains('text-danger')) {
            icon.classList.remove('text-danger');
            icon.classList.add('text-muted');
            showNotification('已取消喜欢', 'info');
        } else {
            icon.classList.remove('text-muted');
            icon.classList.add('text-danger');
            // 添加心跳动画
            icon.style.animation = 'pulse 0.5s';
            setTimeout(() => {
                icon.style.animation = '';
            }, 500);
            showNotification('已添加到喜欢', 'success');
        }
    });
    
    // 分享功能（示例）
    document.querySelector('.bi-share').parentElement.addEventListener('click', function(e) {
        e.preventDefault();
        const currentQuote = quoteText.textContent;
        const currentCategory = quoteCategory.textContent.trim();
        
        const shareText = `【${currentCategory}】${currentQuote}\n\n—— 来自恋爱观与情商小贴士`;
        
        if (navigator.share) {
            navigator.share({
                title: '恋爱观与情商小贴士',
                text: shareText,
                url: window.location.href
            }).catch(err => console.log('分享失败', err));
        } else {
            // 复制到剪贴板
            navigator.clipboard.writeText(shareText).then(() => {
                showNotification('语录已复制到剪贴板', 'success');
            }).catch(() => {
                showNotification('复制失败，请手动复制', 'warning');
            });
        }
    });
    
    // Fetch initial quote
    fetchQuote();
    
    // Start countdown
    startCountdown();
});
