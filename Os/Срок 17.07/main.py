#"Hello 'World'!"
#'Hello, "World"!'

#"""
#Hello "World"
#Hello 'World'
#"""

a = "Hello, "
b = 'World!'

# # Операции над строками

# # 1. Конкатенация (сложение) строк
c = a+b
# print(c)

# # 2. Дублирование (повторение)

# print(c*10)

# # 3. Длина строки (или массива)

# l = len(c)
# print(l)

# # 4. Доступ по индексу

# print(c[0])
# print(c[12])
# print(c[5])
# print(c[-3])

# # 5. Срезы строк
# # str[X:Y:S], 
# где X начальный индекс среза, 
# а Y - окончание среза
# S - шаг
# # str[0, len(str)] -> str[0, len(str)-1]

# 
# print(c)
# print(c[3:9])
c = "А буду я у дуба".lower()
print(c)
print(c[::-1])
print("".join(c.split(" ")))
print("".join(c[::-1].split(" ")))
print("".join(c.split(" ")) == "".join(c[::-1].split(" ")))

# # 6. Неизменяемость строк
# s = "spam"
# #s[1] = 'b'

# # 7. Разбиение строк по разделителю (split())
# tmp = "Мама мыла раму ма"
# print(tmp.split(" "))
# print(tmp.lower().split("м", 1))

# # 8. Поиск в строке
# # str.find(substr, start, end) -> str.find(substr, 0, len(str)-1)
# print(tmp.find("ма"))
# print(tmp.find("ма", 4, 12))
# print(tmp.find("мать"))

# # 9. Преобразование числа в символ
# k = chr(1024)
# print(k)

# Массивы
# 1. Сложение массивов
# lst1 = [1,2,3,4]
# lst2 = [10,2,3,9]
# lst3 = []
# print(lst1+lst2)

# # 2. "Правильное" сложение массивов или добавление элементов
# # lst1.append(lst2)
# lst3.append(lst2)
# print(lst1)
# print(lst3)

# # 3. Обращение по индексу, слайсинг, find() -> см. строки

# # 4. Расширение списка (extend())
# lst1.extend(lst2)
# print(lst1)

# # 5. Вставка элемента в список по указанному индексу (insert())
# lst1.insert(1, 15)
# print(lst1)

# # 6. Удаление элемента списка по значению (remove())
# # метод remove() удаляет только ПЕРВЫЙ найденный элемент
# lst1.remove(3)
# print(lst1)

# # 7. Метод получение элемента из списка + удаление элемента из списка
# # list.pop(index) -> list[index]:element
# elem = lst1.pop(1)
# print(elem, lst1)