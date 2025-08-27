const mainBlock = document.getElementById("main");
const modal = document.getElementById("modal");
const modalImg = document.getElementById("modal-image");
const modalClose = document.getElementById("modal-close");
let initial_page = 0;
let current_page = 0;
let max_page = 3;
let gallery;

const page0 = [
    {src: "abstract-colorful-geometric-overlapping-background-and-texture-free-vector.jpg"},
    {src: "photo-1636955840493-f43a02bfa064.jpg"},
    {src: "ori_4282839_nxi62tsnlas8lqo5a7mxuwirhtm5tl66dbd018n5_minimal-abstract-background-graphic-design-in-neon-colors-trendy-retr.jpg"},
    {src: "images.jpg"},
    {src: "colorful-abstract-background-rra8u4adw1ubypzl.jpg"}
]

const page1 = [
    {src: "abstract-geometric-background-in-flat-design-free-vector.jpg"},
    {src: "images (1).jpg"}
]

const page2 = [
    {src: "360_F_489682374_ckc0OVyT6Av0NGcuYbwBSCxy62blF4CQ.jpg"}
]

// Массив с объектами фотографий
const photos = [page0, page1, page2]

// let content = {"text": ["div", "value1"], "text_add": ["div", "value2"]...}

function loadContent(content_to_load){
    mainBlock.innerHTML = "";
    for (key in content_to_load){
        const newElement = document.createElement(content_to_load[key][0]);
        newElement.innerHTML = content_to_load[key][1];
        newElement.setAttribute("id", key);
        mainBlock.appendChild(newElement);
    }
}

function loadMain(){
    let content = {
        "test": [
            "div", 
            `
            <h1 class="header-text">
                Это мой контент, выгружающийся из JS
            </h1>
            <div class="main-text">
                Здесь расположен текст, автоматически выгружающийся из
                скрипта, чтобы упростить работу конструирования и размещения
                контента на странице. Делается это не очень сложно, вам просто надо:
            </div>
            <ul class="main-list">
                <li>Создать файл расширения .js в своем проекте.</li>
                <li>
                    Написать в нем функцию, которая будет принимать в качестве аргумента
                    объект, в котором содержится HTML код.
                </li>
                <li>
                    Выгрузить этот код на страницу, после загрузки скрипта.
                </li>
            </ul>
            `
        ]
    }
    return content
}

function loadAbout(){
    let content = {
        "test": [
            "div", 
            `
            <h1 class="header-text">
                Это мой блок О нас
            </h1>
            `
        ]
    }
    return content;
}

function loadExcellent(){
    let content = {
        "test": [
            "div", 
            `
            <h1 class="header-text">
                Это мой блок Преимущества
            </h1>
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
            <h1 class="header-text">
                Это мой блок Контакты
            </h1>
            `
        ]
    }
    return content;
}

function next_page(){
    if (current_page + 1 < max_page){
        current_page += 1;
        loadPhotos(photos[current_page]);
    }
}

function back_page(){
    if (current_page - 1 >= initial_page){
        current_page -= 1;
        loadPhotos(photos[current_page]);
    }
}

function loadGallery(){
    let content = {
        "gallery": ["div", `
            <div class="gallery-panel">
                <a href="#" onclick="back_page()" class="gallery-button">Назад</a>
                <a href="#" onclick="next_page()" class="gallery-button">Вперед</a>
            </div>
            <div class="gallery-photos" id="gallery-photos">
            </div>    
        `],
    }
    return content;
}

function contentLoader(content_type){
    let tmp;
    if (content_type == "mainContent"){
        tmp = loadMain();
    } else if (content_type == "aboutContent"){
        tmp = loadAbout();
    } else if (content_type == "excellentContent"){
        tmp = loadExcellent();
    } else if (content_type == "contactsContent"){
        tmp = loadContacts();
    } else if (content_type == "galleryContent"){
        tmp = loadGallery();
    } else { return; }

    loadContent(tmp);

    if (content_type == "galleryContent"){
        gallery = document.getElementById("gallery-photos");
        loadPhotos(photos[current_page]);
    }
}

function loadPhotos(photos){
    gallery.innerHTML = "";
    photos.forEach(photo => {
        // Создание контейнера, фото и размещение фотографии в картинке
        const photoBlock = document.createElement("div");
        photoBlock.className = "photo";
        const imageBlock = document.createElement("img");
        imageBlock.src = photo.src;
        photoBlock.appendChild(imageBlock);
        //-------------------------------------------------------------
        // Добавление события onclick() для контейнеров
        photoBlock.onclick = () => {
            modal.style.display = 'flex';
            modalImg.src = photo.src;
        }
        gallery.appendChild(photoBlock);
        // prekol() - вызов функции prekol и обработка результата её выполнения
        // prekol - обращение к функции, для изменения, уточнения, переопределения
        // изначальных инструкций фукнции. В самом простейшем случае вы просто
        // получите адресс в памяти, где находятся инструкции фукнции.
    })
}

modalClose.onclick = () => {
    modal.style.display = 'none';
    modalImg.src = '';
}

modal.onclick = (e) => {
    if (e.target == modal){
        modal.style.display = 'none';
        modalImg.src = '';
    }
}

loadContent(loadMain());