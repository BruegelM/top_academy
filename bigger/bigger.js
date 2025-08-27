// Функция для вычисления наибольшего общего делителя (НОД)
const gcd = (a, b) => {
    // Преобразуем входные числа в положительные
    a = Math.abs(a);
    b = Math.abs(b);
    // Алгоритм Евклида
    return b ? gcd(b, a % b) : a;
};

// Обработчик события нажатия на кнопку "Вычислить НОД"
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем обработчик события focus для полей ввода, чтобы очищать их при фокусе
    document.getElementById('number1').addEventListener('focus', function() {
        this.value = '';
    });
    
    document.getElementById('number2').addEventListener('focus', function() {
        this.value = '';
    });
    
    document.getElementById('calculate').addEventListener('click', function() {
        // Получаем значения из полей ввода
        const num1 = parseInt(document.getElementById('number1').value);
        const num2 = parseInt(document.getElementById('number2').value);
        
        // Проверяем, что введены числа
        if (isNaN(num1) || isNaN(num2)) {
            alert('Пожалуйста, введите корректные числа');
            return;
        }
        
        // Вычисляем НОД с помощью функции gcd
        const result = gcd(num1, num2);
        
        // Отображаем результат
        const resultElement = document.getElementById('result');
        resultElement.textContent = `НОД(${num1}, ${num2}) = ${result}`;
        resultElement.style.display = 'block';
    });
});
