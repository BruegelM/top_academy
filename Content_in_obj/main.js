const mainBlock = document.getElementById("main");
const modal = document.getElementById("modal");
const modalImg = document.getElementById("modal-img");
const modalClose = document.getElementById("modal-close");
let initial_page = 0;
let current_page = 0;
let max_page = 3;
let gallery;

const page0 = [
    {src: "Screenshot1.png"},
    {src: "Screenshot2.png"},
    {src: "Screenshot3.png"},
    {src: "Screenshot4.png"},
    {src: "Screenshot13.png"}
]

const page1 = [
    {src: "Screenshot5.png"},
    {src: "Screenshot6.png"},
    {src: "Screenshot7.png"},
    {src: "Screenshot8.png"},
    {src: "Screenshot14.png"}
]

const page2 = [
    {src: "Screenshot9.png"},
    {src: "Screenshot10.png"},
    {src: "Screenshot11.png"},
    {src: "Screenshot12.png"},
    {src: "Screenshot15.png"}
]

// массив с объектами фотографий
const photos = [page0, page1, page2]

    /* content = {
        "objId": ["tag", "HTML_code"],
        ...
        "objId": ["tag", "HTML_code"],
    }
    */
function loadContent(content) {
    mainBlock.innerHTML = "";
    for (const key in content){
        // content[key] => ["tag", "HTML_code"]
        // ['tag', 'HTML_code'][0] => "tag"
        // ['tag', 'HTML_code'][1] => "HTML_code"
        const newElement = document.createElement(content[key][0]);
        newElement.innerHTML = content[key][1];
        newElement.setAttribute("id", key);
        mainBlock.appendChild(newElement);
    }
}


function loadMain(){
        let content = {
            "test": [
    "div",
    `
    <div class="cards">
        <div class="card" onclick="this.classList.toggle('flipped')">
            <div class="card-inner">
                <div class="card-front">
                    <div class="card-header">Дойти до конца</div>
                    <div class="card-ico">👾</div>
                    <div class="card-text">Ходить регулярно и не бросить</div>
                </div>
                <div class="card-back">
                    <div class="card-text">Не мытьем, так катаньем</div>
                </div>
            </div>
        </div>
        
            <div class="card" onclick="this.classList.toggle('flipped')">
                <div class="card-inner">
                    <div class="card-front">
                        <div class="card-header">Понять</div>
                        <div class="card-ico">🧠</div>
                        <div class="card-text">Научиться понимать 100% кода, который возвращает GPT. С фокусом на бекендную логику.</div>
                    </div>
                    <div class="card-back">
                        <div class="card-text">Поймет тот, кто хочет понять</div>
                    </div>
                </div>
            </div>
        
                <div class="card" onclick="this.classList.toggle('flipped')">
                    <div class="card-inner">
                        <div class="card-front">
                            <div class="card-header">Суметь</div>
                            <div class="card-ico">🤖</div>
                            <div class="card-text">Написать наконец свою LLM, в коде которой мне все понятно</div>
                        </div>
                        <div class="card-back">
                            <div class="card-text">Текст на обратной стороне</div>
                        </div>
                    </div>
                </div>
        </div>

    `
    ]}
    return content;
}

function loadAbout(){
    let content = {
        "test": [
            "div",
            `
            <div class="tasks">
    <div class="task">
        <div class="task-ico">🧑‍🦯</div>
        <div class="task-header">Ходить каждый день</div>
        <div class="task-text">Ходить на учёбу каждый день — это ключевой элемент на пути к успеху. Регулярное посещение занятий формирует дисциплину, которая необходима для достижения любых целей. Каждый день в учебном процессе — это возможность получить новые знания, развить навыки и углубить понимание предмета. Пропуская занятия, мы теряем важные части мозаики, из которых складывается общая картина. </div>
    </div>
    <div class="task">
        <div class="task-ico">🧙</div>
        <div class="task-header">Делать домашку</div>
        <div class="task-text">Выполнение домашнего задания — это один из важнейших элементов процесса обучения, который помогает глубже понять предмет и усвоить его в полной мере. Домашняя работа позволяет закрепить знания, полученные на уроках, и применить их на практике. Ведь просто слушать преподавателя недостаточно — важно самостоятельно проработать материал, чтобы он остался в памяти. </div>
    </div>
    <div class="task">
        <div class="task-ico">🚀</div>
        <div class="task-header">Дорогу осилит идущий</div>
        <div class="task-text">Важно продолжать каждый день хотя бы по немногу писать код и пытаться понять его, пытаться выстраивать логические цепочки, продолжать использовать GPT и продолжать пытаться его понять</div>
    </div>
</div>
`
        ]
    }
    return content;
}

function loadAdvantages(){
    let content = {
        "test": [
            "div",
            `
            <div class="advantages">
                <div class="advantage">
                    <div class="advantage-ico">⚡</div>
                    <div class="advantage-header">Скорость</div>
                    <div class="advantage-text">Наша платформа работает молниеносно быстро, обеспечивая мгновенный доступ к информации и функциям. Вы не тратите время на ожидание загрузки страниц или обработку запросов. Благодаря оптимизированному коду и современным технологиям, все операции выполняются за доли секунды.</div>
                </div>
                <div class="advantage">
                    <div class="advantage-ico">🔒</div>
                    <div class="advantage-header">Безопасность</div>
                    <div class="advantage-text">Мы уделяем особое внимание защите ваших данных. Наша система использует передовые методы шифрования и многоуровневую аутентификацию, чтобы гарантировать конфиденциальность и целостность информации. Вы можете быть уверены, что ваши данные находятся под надежной защитой.</div>
                </div>
                <div class="advantage">
                    <div class="advantage-ico">🎯</div>
                    <div class="advantage-header">Точность</div>
                    <div class="advantage-text">Наши алгоритмы обеспечивают высокую точность результатов. Благодаря постоянному совершенствованию и обучению системы, мы достигаем максимальной релевантности и минимизируем возможность ошибок. Вы всегда получаете именно то, что искали.</div>
                </div>
            </div>
            `
        ]
    }
    return content;
}

function loadContacts(){
    let content = {
        "test": [
            "div",
            `
            <div class="contacts">
                <div class="contact-form">
                    <h2>Свяжитесь с нами</h2>
                    <form>
                        <div class="form-group">
                            <label for="name">Имя:</label>
                            <input type="text" id="name" name="name" placeholder="Введите ваше имя">
                        </div>
                        <div class="form-group">
                            <label for="email">Email:</label>
                            <input type="email" id="email" name="email" placeholder="Введите ваш email">
                        </div>
                        <div class="form-group">
                            <label for="message">Сообщение:</label>
                            <textarea id="message" name="message" placeholder="Введите ваше сообщение"></textarea>
                        </div>
                        <button type="submit" class="submit-btn">Отправить</button>
                    </form>
                </div>
                <div class="contact-info">
                    <h2>Наши контакты</h2>
                    <div class="info-item">
                        <div class="info-ico">📱</div>
                        <div class="info-text">+7 (123) 456-78-90</div>
                    </div>
                    <div class="info-item">
                        <div class="info-ico">✉️</div>
                        <div class="info-text">info@example.com</div>
                    </div>
                    <div class="info-item">
                        <div class="info-ico">📍</div>
                        <div class="info-text">г. Москва, ул. Примерная, д. 123</div>
                    </div>
                </div>
            </div>
            `
        ]
    }
    return content;
}

function next_page (){
    if (current_page + 1 < max_page){
        current_page += 1;
        loadPhotos(photos[current_page]);
    }
    console.log(current_page);
}

function back_page(){
    if (current_page - 1 >= initial_page){
        current_page -= 1;
        loadPhotos(photos[current_page]);
    }
    console.log(current_page);
}

function loadGallery(){
    let content = {
        "gallery": ["div", `<div class="photos-container"</div>
        <div class="gallery-panel">    
            <a href ="#" onclick="back_page()" class="gallery-arrow">◀︎</a>
            <a href ="#" onclick="next_page()" class="gallery-arrow">▶︎</a>
            </div>
            <div class="gallery-photos" id="gallery-photos">
            </div>
            `]
    }
    return content;
}

// Инициализация страницы
document.addEventListener('DOMContentLoaded', function() {
    // Обработчик закрытия модального окна
    modalClose.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    // Загрузка главной страницы при запуске
    loadContent(loadMain());
    
    // Добавление обработчиков событий для кнопок меню
    document.getElementById('home-button').addEventListener('click', function(e) {
        e.preventDefault();
        contentLoader('home-button');
    });
    
    document.getElementById('about-button').addEventListener('click', function(e) {
        e.preventDefault();
        contentLoader('about-button');
    });
    
    document.getElementById('advantages-button').addEventListener('click', function(e) {
        e.preventDefault();
        contentLoader('advantages-button');
    });
    
    document.getElementById('contacts-button').addEventListener('click', function(e) {
        e.preventDefault();
        contentLoader('contacts-button');
    });
    
    document.getElementById('gallery-button').addEventListener('click', function(e) {
        e.preventDefault();
        contentLoader('gallery-button');
    });
});

function contentLoader(content_type){
    let tmp;
    if (content_type == "home-button"){
        tmp = loadMain();
    } else if (content_type == "about-button"){
        tmp = loadAbout();
    } else if (content_type == "advantages-button"){
        tmp = loadAdvantages();
    } else if (content_type == "contacts-button"){
        tmp = loadContacts();
    } else if (content_type == "gallery-button"){
        tmp = loadGallery();
    } else {return; }


    loadContent(tmp);
    if (content_type == "gallery-button"){
        gallery = document.getElementById("gallery-photos");
        loadPhotos(photos[current_page]);
    }
}

function loadPhotos(photos){
    gallery.innerHTML = "";
    photos.forEach(photo => {
        // создание контейнера, фото и размещения фотографии в картинке + атрибут пути
        const photoBlock = document.createElement("div");
        photoBlock.className = "photo";
        const imageBlock = document.createElement("img");
        imageBlock.src = photo.src;
        photoBlock.appendChild(imageBlock);
        // добавление события onclick() для контейнера
        photoBlock.onclick = () => {
        // prekol() - вызов функции prekol и обработка результата вызова функции
        // prekol = () - обращение к функции для изменения уточнения переопределения 
        // изначальных функций. В самом простейшем случае вы просто 
        // получите адресс памяти где находится инструкции функции
            modal.style.display = 'flex'; 
            // Создаем контейнер для изображения и крестика
            const imgContainer = document.createElement("div");
            imgContainer.id = "modal-img-container";
            
            modalImg.src = photo.src;
            
            // Создаем крестик закрытия
            const closeBtn = document.createElement("div");
            closeBtn.id = "modal-close";
            closeBtn.innerHTML = "×";
            closeBtn.onclick = function(e) {
                e.stopPropagation();
                modal.style.display = 'none';
                }
            };

        modal.onclick = (e) => {
            if (e.target == modal){
                    modal.style.display = 'none';
                    modalImg.src = '';
            }


            // Добавляем элементы в DOM
            imgContainer.appendChild(modalImg);
            imgContainer.appendChild(closeBtn);
            modal.innerHTML = '';
            modal.appendChild(imgContainer);
        }
        gallery.appendChild(photoBlock);
    })
}

const content = loadMain();
loadContent(content);