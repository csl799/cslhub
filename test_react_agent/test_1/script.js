// 游戏配置
const GRID_SIZE = 20;
const CELL_SIZE = 20;
const CANVAS_SIZE = GRID_SIZE * CELL_SIZE;

// 游戏状态
let snake = [
    {x: 10, y: 10},
    {x: 9, y: 10},
    {x: 8, y: 10}
];
let food = {x: 15, y: 10};
let direction = 'RIGHT';
let nextDirection = 'RIGHT';
let score = 0;
let highScore = localStorage.getItem('snakeHighScore') || 0;
let gameRunning = false;
let gameLoop = null;
let speed = 150;

// DOM元素
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('score');
const highScoreElement = document.getElementById('highScore');
const gameOverElement = document.getElementById('gameOver');
const startBtn = document.getElementById('startBtn');
const restartBtn = document.getElementById('restartBtn');

// 初始化
function init() {
    canvas.width = CANVAS_SIZE;
    canvas.height = CANVAS_SIZE;
    highScoreElement.textContent = highScore;
    generateFood();
    draw();
}

// 生成食物
function generateFood() {
    do {
        food = {
            x: Math.floor(Math.random() * GRID_SIZE),
            y: Math.floor(Math.random() * GRID_SIZE)
        };
    } while (snake.some(segment => segment.x === food.x && segment.y === food.y));
}

// 绘制游戏
function draw() {
    ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
    
    // 绘制网格
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= GRID_SIZE; i++) {
        ctx.beginPath();
        ctx.moveTo(i * CELL_SIZE, 0);
        ctx.lineTo(i * CELL_SIZE, CANVAS_SIZE);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, i * CELL_SIZE);
        ctx.lineTo(CANVAS_SIZE, i * CELL_SIZE);
        ctx.stroke();
    }
    
    // 绘制蛇
    snake.forEach((segment, index) => {
        const gradient = ctx.createRadialGradient(
            segment.x * CELL_SIZE + CELL_SIZE/2,
            segment.y * CELL_SIZE + CELL_SIZE/2,
            0,
            segment.x * CELL_SIZE + CELL_SIZE/2,
            segment.y * CELL_SIZE + CELL_SIZE/2,
            CELL_SIZE/2
        );
        
        if (index === 0) {
            // 蛇头
            gradient.addColorStop(0, '#4CAF50');
            gradient.addColorStop(1, '#2E7D32');
            ctx.fillStyle = gradient;
            ctx.shadowBlur = 8;
            ctx.shadowColor = '#4CAF50';
        } else {
            // 蛇身
            gradient.addColorStop(0, '#66BB6A');
            gradient.addColorStop(1, '#43A047');
            ctx.fillStyle = gradient;
            ctx.shadowBlur = 4;
            ctx.shadowColor = '#66BB6A';
        }
        
        ctx.fillRect(
            segment.x * CELL_SIZE + 1,
            segment.y * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2
        );
        
        // 蛇头眼睛
        if (index === 0) {
            ctx.shadowBlur = 0;
            ctx.fillStyle = 'white';
            const eyeSize = 3;
            const eyeOffset = 5;
            
            if (direction === 'RIGHT') {
                ctx.fillRect(segment.x * CELL_SIZE + 13, segment.y * CELL_SIZE + 4, eyeSize, eyeSize);
                ctx.fillRect(segment.x * CELL_SIZE + 13, segment.y * CELL_SIZE + 12, eyeSize, eyeSize);
            } else if (direction === 'LEFT') {
                ctx.fillRect(segment.x * CELL_SIZE + 3, segment.y * CELL_SIZE + 4, eyeSize, eyeSize);
                ctx.fillRect(segment.x * CELL_SIZE + 3, segment.y * CELL_SIZE + 12, eyeSize, eyeSize);
            } else if (direction === 'UP') {
                ctx.fillRect(segment.x * CELL_SIZE + 4, segment.y * CELL_SIZE + 3, eyeSize, eyeSize);
                ctx.fillRect(segment.x * CELL_SIZE + 12, segment.y * CELL_SIZE + 3, eyeSize, eyeSize);
            } else if (direction === 'DOWN') {
                ctx.fillRect(segment.x * CELL_SIZE + 4, segment.y * CELL_SIZE + 13, eyeSize, eyeSize);
                ctx.fillRect(segment.x * CELL_SIZE + 12, segment.y * CELL_SIZE + 13, eyeSize, eyeSize);
            }
        }
    });
    
    // 绘制食物
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#f44336';
    
    const foodGradient = ctx.createRadialGradient(
        food.x * CELL_SIZE + CELL_SIZE/2,
        food.y * CELL_SIZE + CELL_SIZE/2,
        0,
        food.x * CELL_SIZE + CELL_SIZE/2,
        food.y * CELL_SIZE + CELL_SIZE/2,
        CELL_SIZE/2
    );
    foodGradient.addColorStop(0, '#ff6b6b');
    foodGradient.addColorStop(1, '#f44336');
    ctx.fillStyle = foodGradient;
    
    ctx.beginPath();
    ctx.arc(
        food.x * CELL_SIZE + CELL_SIZE/2,
        food.y * CELL_SIZE + CELL_SIZE/2,
        CELL_SIZE/2 - 2,
        0,
        Math.PI * 2
    );
    ctx.fill();
    
    // 食物上的高光
    ctx.shadowBlur = 0;
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.beginPath();
    ctx.arc(
        food.x * CELL_SIZE + CELL_SIZE/2 - 3,
        food.y * CELL_SIZE + CELL_SIZE/2 - 3,
        3,
        0,
        Math.PI * 2
    );
    ctx.fill();
    
    // 重置阴影
    ctx.shadowBlur = 0;
}

// 移动蛇
function move() {
    direction = nextDirection;
    
    const head = {...snake[0]};
    
    switch (direction) {
        case 'RIGHT':
            head.x += 1;
            break;
        case 'LEFT':
            head.x -= 1;
            break;
        case 'UP':
            head.y -= 1;
            break;
        case 'DOWN':
            head.y += 1;
            break;
    }
    
    // 检查是否吃到食物
    if (head.x === food.x && head.y === food.y) {
        snake.unshift(head);
        score += 10;
        scoreElement.textContent = score;
        generateFood();
        
        // 加速
        if (speed > 60) {
            speed -= 2;
        }
        
        // 更新最高分
        if (score > highScore) {
            highScore = score;
            highScoreElement.textContent = highScore;
            localStorage.setItem('snakeHighScore', highScore);
        }
    } else {
        snake.unshift(head);
        snake.pop();
    }
    
    draw();
}

// 检查碰撞
function checkCollision() {
    const head = snake[0];
    
    // 撞墙
    if (head.x < 0 || head.x >= GRID_SIZE || head.y < 0 || head.y >= GRID_SIZE) {
        return true;
    }
    
    // 撞自身
    for (let i = 1; i < snake.length; i++) {
        if (snake[i].x === head.x && snake[i].y === head.y) {
            return true;
        }
    }
    
    return false;
}

// 游戏循环
function gameStep() {
    if (!gameRunning) return;
    
    if (checkCollision()) {
        gameOver();
        return;
    }
    
    move();
}

// 开始游戏
function startGame() {
    if (gameRunning) return;
    
    // 重置游戏
    snake = [
        {x: 10, y: 10},
        {x: 9, y: 10},
        {x: 8, y: 10}
    ];
    direction = 'RIGHT';
    nextDirection = 'RIGHT';
    score = 0;
    speed = 150;
    scoreElement.textContent = '0';
    gameOverElement.textContent = '';
    gameRunning = true;
    
    startBtn.disabled = true;
    restartBtn.disabled = false;
    
    generateFood();
    draw();
    
    gameLoop = setInterval(gameStep, speed);
}

// 游戏结束
function gameOver() {
    gameRunning = false;
    clearInterval(gameLoop);
    gameOverElement.textContent = '游戏结束! 得分: ' + score;
    startBtn.disabled = false;
    restartBtn.disabled = true;
    
    // 闪烁效果
    let blinkCount = 0;
    const blinkInterval = setInterval(() => {
        if (blinkCount >= 6) {
            clearInterval(blinkInterval);
            draw();
            return;
        }
        if (blinkCount % 2 === 0) {
            ctx.fillStyle = 'rgba(244, 67, 54, 0.3)';
            ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
        } else {
            draw();
        }
        blinkCount++;
    }, 300);
}

// 键盘控制
document.addEventListener('keydown', (e) => {
    if (!gameRunning) return;
    
    const key = e.key;
    e.preventDefault();
    
    if ((key === 'ArrowUp' || key === 'w' || key === 'W') && direction !== 'DOWN') {
        nextDirection = 'UP';
    } else if ((key === 'ArrowDown' || key === 's' || key === 'S') && direction !== 'UP') {
        nextDirection = 'DOWN';
    } else if ((key === 'ArrowLeft' || key === 'a' || key === 'A') && direction !== 'RIGHT') {
        nextDirection = 'LEFT';
    } else if ((key === 'ArrowRight' || key === 'd' || key === 'D') && direction !== 'LEFT') {
        nextDirection = 'RIGHT';
    }
});

// 触摸控制
let touchStartX = 0;
let touchStartY = 0;

canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    const touch = e.touches[0];
    touchStartX = touch.clientX;
    touchStartY = touch.clientY;
});

canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
}, {passive: false});

canvas.addEventListener('touchend', (e) => {
    e.preventDefault();
    if (!gameRunning || !touchStartX || !touchStartY) return;
    
    const touchEnd = e.changedTouches[0];
    const dx = touchEnd.clientX - touchStartX;
    const dy = touchEnd.clientY - touchStartY;
    
    if (Math.abs(dx) > Math.abs(dy)) {
        // 水平滑动
        if (dx > 0 && direction !== 'LEFT') {
            nextDirection = 'RIGHT';
        } else if (dx < 0 && direction !== 'RIGHT') {
            nextDirection = 'LEFT';
        }
    } else {
        // 垂直滑动
        if (dy > 0 && direction !== 'UP') {
            nextDirection = 'DOWN';
        } else if (dy < 0 && direction !== 'DOWN') {
            nextDirection = 'UP';
        }
    }
    
    touchStartX = 0;
    touchStartY = 0;
});

// 按钮事件
startBtn.addEventListener('click', startGame);
restartBtn.addEventListener('click', startGame);

// 限制页面滚动
window.addEventListener('keydown', (e) => {
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
        e.preventDefault();
    }
});

// 页面加载完成时初始化
document.addEventListener('DOMContentLoaded', init);