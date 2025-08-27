# #----------------------------------------------
# # #Выводим пользователю просьбу ввести что-то в консоль
# # print("Введите сюда какой-нибудь текст:\n")

# # #Получаем данные со входа (из консоли)
# # inpt = input()

# # #Выводим полученную строку в верхнем регистре
# # print(inpt.upper())

# # print("Hello, World".__dir__())
# #----------------------------------------------

# # Программа для вычисления ряда чисел Фибоначчи

# # Создадим начальные переменные
# fib1 = 1
# fib2 = 1

# # Попросим пользователя ввести длину ряда чисел
# n = int(input())

# # Зададим простой цикл for для подсчета ряда
# print("Ряд с помощью цикла for:")
# # range(2,n) -> (2,3,4,5,6,7,...n)
# # +-> end_ptr = 123857432875
# for i in range(2, n):
#     fib_sum = fib1 + fib2
#     fib1 = fib2
#     fib2 = fib_sum
#     print(fib2, end=' ')

# # js {} - обособленный участок кода
# # python : - обособленный участок кода

# # Зададим простой цикл while для подсчета ряда
# print("\nРяд с помощью цикла while:")
# # range(2,n) -> (2,3,4,5,6,7,...n)
# # +-> end_ptr = 123857432875
# while n > 0:
#     fib_sum = fib1 + fib2
#     fib1 = fib2
#     fib2 = fib_sum
#     n -= 1
#     print(fib2, end=' ')

# Занятие 2

## Типы данных

# i = 5 # (int, Integer)
# print(type(i))
# f = 1.05 # (float)
# print(type(f))
# s = "Я строка" # (str, String)
# print(type(s))
# l = [5, "hello", [], {}] # (list)
# print(type(l))
# d = {1: "Hello", "world": 2, s: l} # (dict, Dictionary)
# print(type(d))
# t = (1, 3, "aaa", "bbb", d) # (tuple)
# print(type(t))
# i_set = set([1, 2, 3, 4, 5]) # (set)
# print(type(i_set))

# print("Введите два числа:")
# try:
#     a = float(input("Первое число: "))
#     b = float(input("Второе число: "))
#     print (a/b)
# except ValueError:
#     a = 0.0
#     b = 0.0
# except ZeroDivisionError:
#     print (a/1)

# try:
#     some code
# except:
#     some code on Exception

# print(a+b)

import random

comp = random.randint(1, 10)
flag = True

while flag:
    # Получаем на вход строку с числом или командой выхода
    a = input("Введите число: ")
    # Если пользователь ввел слово 'exit' - завершаем выполнение
    if a == "exit":
        flag = False
        break
    # Введем конструкцию проверки на наличие ошибки при преобразовании введенной строки в число
    try:
        a = int(a)
    except ValueError:
        a = 0
    # Проверяем условие победы
    if a == comp:
        print("Поздравляю, вы угадали! Это было число: ", comp)
        flag = False
        break
    print("Попробуйте ещё раз ;(")

# Задание 3
# Напишите программу, вычисляющую площадь ромба. Пользователь с клавиатуры вводит длину двух его
# диагоналей.
