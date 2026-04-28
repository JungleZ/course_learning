// DISC领导力测试题目
const questions = [
    { id: 1, question: "在团队会议中，我倾向于主动提出想法和建议", type: "D" },
    { id: 2, question: "我喜欢与团队成员建立良好的人际关系", type: "I" },
    { id: 3, question: "我注重细节，确保所有工作都按照既定标准完成", type: "C" },
    { id: 4, question: "我能够很好地处理突发情况和压力", type: "D" },
    { id: 5, question: "我善于鼓励和支持团队成员", type: "S" },
    { id: 6, question: "我倾向于制定明确的目标和计划", type: "D" },
    { id: 7, question: "我喜欢在轻松愉快的氛围中工作", type: "I" },
    { id: 8, question: "我重视数据和事实，会仔细分析后再做决定", type: "C" },
    { id: 9, question: "我能够耐心倾听他人的意见", type: "S" },
    { id: 10, question: "我愿意承担挑战性的任务和责任", type: "D" },
    { id: 11, question: "我擅长在团队中营造积极的氛围", type: "I" },
    { id: 12, question: "我做事严谨，会反复检查以确保准确性", type: "C" },
    { id: 13, question: "我倾向于维持和谐的工作环境", type: "S" },
    { id: 14, question: "我喜欢推动项目进展，确保按时完成", type: "D" },
    { id: 15, question: "我善于与不同类型的人沟通", type: "I" },
    { id: 16, question: "我重视规则和程序，确保合规性", type: "C" },
    { id: 17, question: "我愿意支持团队成员，帮助他们解决问题", type: "S" },
    { id: 18, question: "我具有强烈的竞争意识，追求卓越", type: "D" },
    { id: 19, question: "我喜欢在团队中分享快乐和成就", type: "I" },
    { id: 20, question: "我做事谨慎，会考虑各种可能性和风险", type: "C" },
    { id: 21, question: "我倾向于稳定的工作节奏，不喜欢频繁变化", type: "S" },
    { id: 22, question: "我经常设定高标准并努力达成", type: "D" },
    { id: 23, question: "我善于发现他人的优点并给予赞美", type: "I" },
    { id: 24, question: "我注重质量控制，会建立详细的标准", type: "C" }
];

// 生成问题HTML
function generateQuestions() {
    const container = document.getElementById('questionsContainer');
    container.innerHTML = '';
    
    questions.forEach((q, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'card question-card';
        questionDiv.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${index + 1}. ${q.question}</h5>
                <div class="btn-group w-100" role="group">
                    <input type="radio" class="btn-check" name="q${q.id}" id="q${q.id}_1" value="1" required>
                    <label class="btn btn-outline-secondary" for="q${q.id}_1">1</label>
                    
                    <input type="radio" class="btn-check" name="q${q.id}" id="q${q.id}_2" value="2" required>
                    <label class="btn btn-outline-secondary" for="q${q.id}_2">2</label>
                    
                    <input type="radio" class="btn-check" name="q${q.id}" id="q${q.id}_3" value="3" required>
                    <label class="btn btn-outline-secondary" for="q${q.id}_3">3</label>
                    
                    <input type="radio" class="btn-check" name="q${q.id}" id="q${q.id}_4" value="4" required>
                    <label class="btn btn-outline-secondary" for="q${q.id}_4">4</label>
                    
                    <input type="radio" class="btn-check" name="q${q.id}" id="q${q.id}_5" value="5" required>
                    <label class="btn btn-outline-secondary" for="q${q.id}_5">5</label>
                </div>
            </div>
        `;
        container.appendChild(questionDiv);
    });
}

// 计算结果
function calculateResults() {
    const answers = [];
    
    questions.forEach(q => {
        const selectedValue = document.querySelector(`input[name="q${q.id}"]:checked`);
        if (selectedValue) {
            answers.push({
                question_id: q.id,
                score: parseInt(selectedValue.value),
                type: q.type
            });
        }
    });
    
    if (answers.length !== questions.length) {
        alert('请完成所有问题后再提交');
        return null;
    }
    
    const scores = { 'D': 0, 'I': 0, 'S': 0, 'C': 0 };
    
    answers.forEach(answer => {
        scores[answer.type] += answer.score;
    });
    
    let dominantType = 'D';
    let maxScore = scores.D;
    
    for (const type in scores) {
        if (scores[type] > maxScore) {
            maxScore = scores[type];
            dominantType = type;
        }
    }
    
    return { scores, dominantType };
}

// 生成结果解释
function getInterpretation(dominantType) {
    const interpretations = {
        'D': {
            style: '支配型 (Dominance)',
            description: '您是一位果断、目标导向的领导者。您喜欢掌控局面，快速决策，并推动项目向前发展。',
            strengths: ['目标导向', '果断决策', '执行力强', '勇于挑战'],
            developmentAreas: ['倾听他人意见', '考虑他人感受', '耐心与细致']
        },
        'I': {
            style: '影响型 (Influence)', 
            description: '您是一位热情、富有感染力的领导者。您善于激励他人，营造积极的团队氛围。',
            strengths: ['沟通能力强', '乐观积极', '鼓舞他人', '建立关系'],
            developmentAreas: ['关注细节', '坚持目标', '处理冲突']
        },
        'S': {
            style: '稳健型 (Steadiness)',
            description: '您是一位稳定、可靠的领导者。您重视团队和谐，善于建立持久的工作关系。',
            strengths: ['耐心可靠', '团队合作', '稳定情绪', '支持他人'],
            developmentAreas: ['接受变化', '推动变革', '果断决策']
        },
        'C': {
            style: '谨慎型 (Compliance)',
            description: '您是一位精确、系统的领导者。您注重质量、标准和准确性。',
            strengths: ['注重细节', '精确严谨', '逻辑性强', '遵守标准'],
            developmentAreas: ['加快决策速度', '灵活应对', '简化流程']
        }
    };
    
    return interpretations[dominantType];
}

// 显示结果
function showResults(results) {
    const { scores, dominantType } = results;
    const interpretation = getInterpretation(dominantType);
    
    document.getElementById('loadingSpinner').style.display = 'none';
    document.getElementById('resultSection').style.display = 'block';
    
    document.getElementById('styleType').textContent = interpretation.style;
    document.getElementById('styleDescription').textContent = interpretation.description;
    
    const strengthsList = document.getElementById('strengthsList');
    strengthsList.innerHTML = '';
    interpretation.strengths.forEach(strength => {
        const li = document.createElement('li');
        li.className = 'strength-item';
        li.textContent = strength;
        strengthsList.appendChild(li);
    });
    
    const developmentAreasList = document.getElementById('developmentAreasList');
    developmentAreasList.innerHTML = '';
    interpretation.developmentAreas.forEach(area => {
        const li = document.createElement('li');
        li.className = 'strength-item';
        li.textContent = area;
        developmentAreasList.appendChild(li);
    });
    
    const scoreDetails = document.getElementById('scoreDetails');
    scoreDetails.innerHTML = `
        <div class="score-display">D (支配): ${scores.D}</div>
        <div class="score-display">I (影响): ${scores.I}</div>
        <div class="score-display">S (稳健): ${scores.S}</div>
        <div class="score-display">C (谨慎): ${scores.C}</div>
    `;
    
    document.getElementById('value-d').textContent = scores.D;
    document.getElementById('value-i').textContent = scores.I;
    document.getElementById('value-s').textContent = scores.S;
    document.getElementById('value-c').textContent = scores.C;
    
    const maxScore = Math.max(...Object.values(scores));
    if(maxScore > 0) {
        document.getElementById('bar-d').style.height = `${(scores.D / maxScore) * 80}%`;
        document.getElementById('bar-i').style.height = `${(scores.I / maxScore) * 80}%`;
        document.getElementById('bar-s').style.height = `${(scores.S / maxScore) * 80}%`;
        document.getElementById('bar-c').style.height = `${(scores.C / maxScore) * 80}%`;
    }
    
    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    generateQuestions();
    
    document.getElementById('testForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        document.getElementById('loadingSpinner').style.display = 'block';
        
        setTimeout(() => {
            const results = calculateResults();
            if (results) {
                showResults(results);
            }
        }, 1000);
    });
});
