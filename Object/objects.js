const objectData = document.getElementById('objectData');
//name.AttributeName - форма обращения к атрибуту объекта любого типа по его имени
// форма обращения к методу по его имени () name.MethodName(argument)
//objectData.textContent = document.ATTRIBUTE_NODE;
console.log(document);

let user = {
    name: 'John',
    surname: 'Petrovich',
    age: 30,
    email: 'john@example.com',
}
/* let [имя переменной] = {
        имя поля: значение поля
        имя поля: значение поля
        имя поля: значение поля
        имя поля: значение поля
    }
*/

// console.log(user);

//создание полей (атрибутов) и проектирование объектов
// дозаполнение обекта после создания

user.address = "Ul. Pushkina, Dom Kolotushkina";

for (key in user){
    objectData.textContent += user[key] + "; ";
}

