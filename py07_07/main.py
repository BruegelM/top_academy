# Строки, списки и массивы

a = "Hello, "
b = "world!"

# 1. Конкатенация строк
#print(a + b)
c =a+b
print(c)
print(ord(a[0]))


# 2. Дублирование (повторение) строки
print(c * 3)


# 3. Длинна строки или массива
l = len(c)
print(l)


# 4. Доступ по индексу
print(c[0])
print(c[7])
print(c[10])

# 5. Срезы строк
# str[0, len(str))] -> str[0, len(str)-1]
print(c[0:5])

# 6. Неизменяемость строк
s = 'spam'
#s[1] = 'b'

# 7. Разбиение строки по разделителю (split())
#print(c.split('l'))

tmp = "Мама мыла раму"
print(tmp.split('м'))
print(tmp.split(' '))
print(tmp.split('а'))

# 8. Поиск по строке
# str.find(substr, start, end) -> str.find(substr, 0, len(str)-1)
print(tmp.find('м', 4, 12))

# 9. Преобразование числа в символ
print(chr(979))

# 10. Массивы
lst1 = [1, 2, 3, 4, 5]
lst2 = ['a', 'b', 'c', 'd', 'e']
print(lst1+lst2)

# правильное сложение массивов
lst1.append(lst2)
print(lst1)

# 11. Обращение по индексу слайсинг, find() -> см строки

# 12. Расширение списка (extend())
lst1.extend(lst2)
print(lst1)

# 13. Вставка элемента в список по указанному индексу
lst1.insert(4, 'a')
print(lst1)

# 14. Удаление из списка по значению (remove())
# метод remove удаляет только первый найденный элемент
lst1.remove('e')
print(lst1)

# 15 Метод получения элемента из списка + удаление элемента из списка
# list.pop(index) -> list[index]:element
elem = lst1.pop(4)
print(elem, lst1)

print(c[-1:])