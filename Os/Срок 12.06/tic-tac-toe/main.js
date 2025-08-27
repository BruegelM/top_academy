const gameBoard = document.getElementById('game');
const statusBar = document.getElementById('status');
const resetButton = document.getElementById('reset-button');
// Создадим массив для хранения состояния игры и заполним его пустым текстом
let board = Array(9).fill('');
// Array(9) = [ , , , , , , , , ]
// fill('') = ['', 'X', '', '', '0', '', 'X', 'X', '']
//              0,   1,  2,  3,   4,  5,   6,   7,  8
// Переменная для хранения текущего игрока
let currentPlayer = 'X';
// Состояние игры
let running = true;
// Переменная для хранения победных комбинаций игры
const winComb = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // Комбинации в строке
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // Комбинации в столбце
    [2, 4, 6], [0, 4, 8]
];

//${} - конструкция форматирования переменных

// Функция для начала игры
function initGame(){
    // Обновляем переменные игры
    board = Array(9).fill('');
    currentPlayer = 'X';
    running = true;
    // Устанавливаем статусбар в начальное значение
    statusBar.textContent = `Ход игрока ${currentPlayer}`;
    // Создаем пустое HTML наполение блока
    gameBoard.innerHTML = '';
    // Запуск цикла на девять итераций
    // Условия цикла for
    //  (итератор; условие выхода; условие шага)
    // итератор - переменная, являющаяся счетчиком цикла
    // ++ - инкремент (увелечение на одну единицу (согласно единице измерения))

    // () - указание на вызов функции, либо на создание условия

    for (let i=0; i<9; i++){
        // Создаем ячейку игрового поля
        const cell = document.createElement('div');
        // Доавление стиля к элементу
        //[html элемент].[обращение к свойству class].добавить('имя класса');
        cell.classList.add('cell');
        // Добавление атрибуета data-index
        // data-index необходим для связывания ячейки и места в таблице
        cell.setAttribute('data-index', i);
        // Добавим атрибут role для установки поведения ячейки
        // как ячейки таблицы
        cell.setAttribute('role', 'gridcell');
        cell.setAttribute('tabindex', 0);
        // Добавляем прослушивание события клика на ячейку
        cell.addEventListener('click', cellClicked);
        // Добавляем полученный div в наше игровое поле
        gameBoard.appendChild(cell);
    }
}

function cellClicked(e){
    // event.target - содержит в себе элемент, над которым проводится действие
    // Element.getAttribute() - получение значения атрибута по его имени
    const index = e.target.getAttribute('data-index');
    // Проверят, если в поле, куда щелкнул игрок уже находится X и 0
    // или игра не была запущена, то функция завершает работу.
    if (board[index] !== '' || !running) { return; }
    updateCell(e.target, index);
    checkWinner();
    // если index = 0, то мы получим значение нулевого элемента board
}

// Метод принимает HTML тег со страницы, на который был совершен клик
// И индекс этого элемента в сетке
function updateCell(cell, index){
    board[index] = currentPlayer;
    cell.textContent = currentPlayer;
    // ДЗ!
    // Проверить, что если currentPlayer == 'X', то объекту cell
    // добавить стиль XPlayerCell (который меняет цвет заднего фона)
    // если currentPlayer == 'O', то объекту cell
    // добавить стиль OPlayerCell (который меняет цвет заднего фона)
    // XPlayerCell и OPlayerCell создать в файлике main.css самостоятельно
    cell.classList.add('disabled');
}

function checkWinner(){
    let roundWon = false;
    for (const combo of winComb){
        const [a, b, c] = combo; // [0, 1, 2]
        /* if (
            board[a] - проверка на наличие в массиве board элемента с индексом a
            board[a] === board[b] - проверка, на равность значения в массиве 
            игры ячейки под индексом a на равность ячейке под индексом b
        )*/
        if (board[a] && board[a] === board[b] && board[a] === board[c]) {
            roundWon = true;
            break;    
        }
    }
    // Если была найдена победная комбинация
    if (roundWon){
        statusBar.textContent = `Победил игрок ${currentPlayer}`;
        running = false;
        return;
    }
    // Если игра завершилась ничьей
    if (!board.includes('')){
        statusBar.textContent = 'Ничья!';
        running = false;
        return;
    }
    // Смена игрока
    if (currentPlayer == 'X') {
        currentPlayer = 'O';
    }
    else{
        currentPlayer = 'X';
    }
}

resetButton.addEventListener('click', ()=>{
    initGame();
})

initGame();