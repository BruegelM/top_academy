# ** - возведение в степень
# // - целочисленное деление
# % - остаток от деления

# 2.6 дано двузначное число
# a) число десятков
# б) число единиц в нем
# в) сумма его цифр
# г) произведение его цифр

# 67 
# a) 6
# б) 7
# в) 13
# г) 42

#Задача 2.6
# number = int(input("Введите двузначное число: "))
# result_a = number // 10
# result_b = number % 10
# result_c = result_a + result_b
# result_d = result_a * result_b
# print(f"Пользователь ввел {number}.\nВ числе {number} хранится {result_a} десятков и {result_b} единиц.\nСумма цифр равна {result_c}.\nПроизведение цифр равно {result_d}.")

#Задача 2.7 Дано дузначное число Получить число, образониванное при перестановке цифр заданного числа
# number = int(input("Введите двузначное число: "))
# digit = number % 10
# tens = number // 10
# number = digit * 10 + tens
# print(number)

#Задача 2.8
# Дано трезначное число, найти: 123
# a) число единиц в нем 3
# б) число десятков 2
# в) сумма его цифр 6
# г) произведение его цифр 6

# number = int(input("Введите трезначное число: "))
# digite = number % 10
# tens = number // 10 % 10
# hundreds = number // 100
# result_a = digite
# result_b = tens
# result_c = digite + tens + hundreds
# result_d = digite * tens * hundreds
# print(f"Пользователь ввел {number}.\nЧисло хранит {result_a} единиц.\nСумма десятков равна {result_b}.\nСумма цифр равно {result_c}.\nПроизведение цифр равно {result_d}.")

#Задача 2.9
# Найти число найленное при прочтении справа на лево

# number = int(input("Введите трезначное число: "))
# digite = number % 10
# tens = number // 10 % 10
# hundreds = number // 100
# result = digite * 100 + tens * 10 + hundreds
# print(result)

#Задача 2.10
# первую цифру перенесли назад
# number = int(input("Введите трезначное число: "))
# digite = number % 10
# tens = number // 10 % 10
# hundreds = number // 100
# result = tens * 100 + digite * 10 + hundreds
# print(result)

#Задача 2.11
# Написать последнюю цифру впереди

# number = int(input("Введите трехначное число: "))
# digite = number % 10
# tens = number // 10 % 10
# hundreds = number // 100
# result = digite * 100 + hundreds * 10 + tens 
# print(result)

#Задача 2.12
# Поменяли первую и вторую цифры
# number = int(input("Введите трехзначное число: "))
# digite = number % 10
# tens = number // 10 % 10
# hundreds = number // 100
# result = digite * 100 + tens * 10 + hundreds
# print(result)

#Задача 2.13
# !!!! доделать до 2.16 включительно !!!!