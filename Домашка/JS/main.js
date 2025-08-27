document.addEventListener('DOMContentLoaded', function() {
    const cButton = document.getElementById('color_button');
    
    cButton.addEventListener('click', function() {
        // Реальная смена цвета (пример)
        document.querySelector('h1').style.color = 
            (document.querySelector('h1').style.color === 'red') ? 'black' : 'red';
        
        // Или ваш alert (но лучше console.log для дебага)
        console.log('Кнопка работает!');
          });
});