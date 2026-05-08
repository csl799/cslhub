const board = document.getElementById('game-board');
const mineCountDisplay = document.getElementById('mine-count');
const timerDisplay = document.getElementById('timer');
const resetBtn = document.getElementById('reset-btn');

let rows = 9, cols = 9, totalMines = 10;
let cells = [];
let minePositions = new Set();
let gameOver = false;
let firstClick = true;
let flagCount = 0;
let timer = 0;
let timerInterval = null;

function initGame() {
    gameOver = false;
    firstClick = true;
    flagCount = 0;
    timer = 0;
    timerDisplay.textContent = '0';
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    minePositions.clear();
    cells = [];
    board.style.gridTemplateColumns = `repeat(${cols}, 36px)`;
    board.innerHTML = '';
    mineCountDisplay.textContent = totalMines;

    for (let r = 0; r < rows; r++) {
        cells[r] = [];
        for (let c = 0; c < cols; c++) {
            const cell = document.createElement('div');
            cell.className = 'cell covered';
            cell.dataset.row = r;
            cell.dataset.col = c;
            cell.dataset.mine = 'false';
            cell.dataset.adjacent = '0';
            cell.dataset.uncovered = 'false';
            cell.dataset.flagged = 'false';

            cell.addEventListener('click', () => handleClick(r, c));
            cell.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                handleRightClick(r, c);
            });

            board.appendChild(cell);
            cells[r][c] = cell;
        }
    }
}

function placeMines(excludeRow, excludeCol) {
    let placed = 0;
    const exclude = new Set();
    for (let dr = -1; dr <= 1; dr++) {
        for (let dc = -1; dc <= 1; dc++) {
            const nr = excludeRow + dr, nc = excludeCol + dc;
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
                exclude.add(nr + ',' + nc);
            }
        }
    }

    while (placed < totalMines) {
        const r = Math.floor(Math.random() * rows);
        const c = Math.floor(Math.random() * cols);
        const key = r + ',' + c;
        if (minePositions.has(key) || exclude.has(key)) continue;
        minePositions.add(key);
        cells[r][c].dataset.mine = 'true';
        placed++;
    }

    // 计算相邻雷数
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (cells[r][c].dataset.mine === 'true') continue;
            let count = 0;
            for (let dr = -1; dr <= 1; dr++) {
                for (let dc = -1; dc <= 1; dc++) {
                    if (dr === 0 && dc === 0) continue;
                    const nr = r + dr, nc = c + dc;
                    if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
                        if (cells[nr][nc].dataset.mine === 'true') count++;
                    }
                }
            }
            cells[r][c].dataset.adjacent = count;
        }
    }
}

function handleClick(r, c) {
    if (gameOver) return;
    const cell = cells[r][c];
    if (cell.dataset.uncovered === 'true' || cell.dataset.flagged === 'true') return;

    if (firstClick) {
        firstClick = false;
        placeMines(r, c);
        timerInterval = setInterval(() => {
            timer++;
            timerDisplay.textContent = timer;
        }, 1000);
    }

    if (cell.dataset.mine === 'true') {
        // 踩雷
        gameOver = true;
        revealAllMines();
        cell.classList.remove('covered');
        cell.classList.add('mine');
        cell.textContent = '💣';
        clearInterval(timerInterval);
        setTimeout(() => alert('游戏结束！你踩到了地雷！'), 100);
        return;
    }

    revealCell(r, c);
    checkWin();
}

function handleRightClick(r, c) {
    if (gameOver) return;
    const cell = cells[r][c];
    if (cell.dataset.uncovered === 'true') return;

    if (cell.dataset.flagged === 'false') {
        cell.dataset.flagged = 'true';
        cell.classList.add('flagged');
        flagCount++;
        mineCountDisplay.textContent = totalMines - flagCount;
    } else {
        cell.dataset.flagged = 'false';
        cell.classList.remove('flagged');
        cell.textContent = '';
        flagCount--;
        mineCountDisplay.textContent = totalMines - flagCount;
    }
}

function revealCell(r, c) {
    const cell = cells[r][c];
    if (cell.dataset.uncovered === 'true' || cell.dataset.flagged === 'true') return;
    if (cell.dataset.mine === 'true') return;

    cell.dataset.uncovered = 'true';
    cell.classList.remove('covered');
    cell.classList.add('uncovered');

    const adjacent = parseInt(cell.dataset.adjacent);
    if (adjacent > 0) {
        cell.textContent = adjacent;
        cell.classList.add('n' + adjacent);
    }

    // 如果是空白格，递归展开周围
    if (adjacent === 0) {
        for (let dr = -1; dr <= 1; dr++) {
            for (let dc = -1; dc <= 1; dc++) {
                if (dr === 0 && dc === 0) continue;
                const nr = r + dr, nc = c + dc;
                if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
                    revealCell(nr, nc);
                }
            }
        }
    }
}

function revealAllMines() {
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            const cell = cells[r][c];
            if (cell.dataset.mine === 'true') {
                cell.classList.remove('covered');
                cell.classList.add('mine');
                cell.textContent = '💣';
            }
        }
    }
}

function checkWin() {
    let uncoveredCount = 0;
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (cells[r][c].dataset.uncovered === 'true') uncoveredCount++;
        }
    }
    const totalSafe = rows * cols - totalMines;
    if (uncoveredCount === totalSafe) {
        gameOver = true;
        clearInterval(timerInterval);
        setTimeout(() => alert('恭喜你赢了！用时 ' + timer + ' 秒'), 100);
    }
}

// 重置游戏
resetBtn.addEventListener('click', () => {
    initGame();
});

initGame();