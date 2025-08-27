const objectData = document.getElementById('objectData');

console.log(document);

// Форма обращения к атрибуту объекта по его имени
// name.AttributeName

// Форма обращения к методу по его имени
// name.MethodName(args?)

// let user = {};  //Создание пустого объекта

// Создание полей (атрибутов) при проектировании объекта
let user = {
    name: "John",
    surname: "Whattson",
    age: 40
}

/*
    let [имя переменной] = {
        [имя поля] : [значение поля],
        [имя поля] : [значение поля],
        [имя поля] : [значение поля],
        [имя поля] : [значение поля],
        ...
        name: "Prekol"
    }
    
    user -> [
        ["name"],
        ["Prekol"]
    ]
*/

// objectData.textContent = user.address;

// Дозаполнение объекта после создания
user.address = "Ul. Pushkina, dom Kolotushkina";

for (key in user){
    objectData.textContent += user[key] + "; ";
}

// 1. В момент прохода циклом по объекту, в качестве
// итератора используются именя полей объекта

// 2. Внутри цикла, обращаться к полям объекта
// можно только по схеме имя_объекта[имя_поля]
