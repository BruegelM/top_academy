
const form = document.getElementById('regForm');
form.addEventListener('submit', function(event) {
    event.preventDefault(); // Отключаем стандартную обработку событий формы
    
    // Собираем данные формы
    const formData = new FormData(form);
    
    // Получаем значения всех полей
    const username = formData.get('login');
    const email = formData.get('email');
    const password = formData.get('password');
    const phone = formData.get('tel');
    const birthDate = formData.get('date');
    const agreement = form.querySelector('.checkbox').checked;
    
    // Выводим в консоль для проверки
    console.log('Форма отправлена!');
    console.log('Логин:', username);
    console.log('Email:', email);
    console.log('Пароль:', password); // В реальном проекте пароль не следует логировать!
    console.log('Телефон:', phone);
    console.log('Дата рождения:', birthDate);
    console.log('Согласие на обработку:', agreement ? 'Да' : 'Нет');
    
    // Здесь можно добавить валидацию данных перед отправкой
    if (!validateForm(username, email, password, phone, birthDate, agreement)) {
        return; // Если валидация не пройдена, прерываем выполнение
    }
    
    // Дальнейшая обработка (например, отправка на сервер)
    // sendFormData(formData);
});

// Функция для базовой валидации формы
function validateForm(username, email, password, phone, date, agreement) {
    if (!username || !email || !password || !phone || !date) {
        console.error('Все поля обязательны для заполнения!');
        return false;
    }
    
    return true; // Все проверки пройдены
}
