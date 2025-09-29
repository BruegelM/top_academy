# # if <булево значение>:

# a = 10

# if a > 5:
#     print(1)
# elif a % 2 == 0: 
#     print(2)
# elif a == 4:
#     print(4)

# else:
#     print(5)

# print(3)

#Task


# m = int (input("Введите первое значение: "))
# n = int (input("Введите первое значение: "))
# if n == 0:
#     print("делить на 0 нельзя")
#     exit()

# if m % n == 0:
#     print (f"Частное от деления {m} на {n} -> {m/n}")

# else:
#     print("m на n нацело не делится")

# #==========================================================
# if m % n == 0 and n != 0:
#     print (f"Частное от деления {m} на {n} -> {m/n}")

# else:
#     print("m на n нацело не делится")

# #==========================================================

# if n != 0:
#     if m % n == 0:
#         print (f"Частное от деления {m} на {n} -> {m/n}")
#     else:
#         print("m на n нацело не делится")
# #==========================================================
# result = "четное" if m % n == 0 else "нечетное"
# print(result)

# number = int(input("Введите дву значное число: "))
# digit = number % 10
# tens = number // 10
# if number**2 == 4*(digit**3 + tens**3):
#     print("равен")
# else:
#     print("не равен")

# num1 = 56
# num2 = -24
# if (abs(num1) > abs(num2)) and num1 < 0:
#     num1 *= 2
# else:
#     num1 /= 2

# print(num1)

# if num2**(1/2) < num1:
#     num2 *= 5

# print(num1)

# num1 = 234
# num2 = 234.23
# num3 = -23
# num4 = -34
# num5 = 0.32
# num6 = 23423.234
# num7 = -2345


# count_negative_number = 0
# if num1 < 0:

# if num2 < 0:

# if num3 < 0:

# if num4 < 0:

# if num5 < 0:

# if num6 < 0:

# if num6 < 0:

# 4.50. Даны три различных целых числа. Определить, какое из них (первое, второе или третье): 
# а) самое большое; 
# б) самое маленькое; 
# в) является средним (средним назовем число, которое больше наименьшего из данных чисел, но меньше наибольшего).

# num1 = 234
# num2 = -123
# num3 = 0.12
# sum_num = num1 + num2 + num3
# num_max = max(num1, num2, num3)
# num_min = min(num1, num2, num3)
# print(f"макс: {num_max}")
# print(f"мин: {num_min}")
# print(f"ср: {sum_num - num_min - num_max}")

# if num2 < num1 and num1 < num3:
#     print(f"{}")
# elif num1 < num2 and num2 < num1:
#     avr = num2
# else:
#     num2 < num3 and num3 < num1
#     avr = num3

# print(avr)

# if num1 < num2 and num1 < num3:
#     min = num1
# elif num2 < num1 and num2 < num3:
#     min = num2
# else:
#     num3 < num1 and num3 < num2
#     min = num3

# print(min)


# if num2 > num1 and num1 > num3:
#     max = num1
# elif num1 > num2 and num2 > num1:
#     max = num2
# else:
#     num2  num3 and num3 < num1
#     max = num3

# print(max)


# 4.48. Определить, в какую из областей (I, II или III — рис. 4.8) попадает точка с заданными координатами. Для простоты принять, что точка не попадает на границы областей.

# a = 45
# b = 12

# if a <= 1:
#     print("I")
# elif 1 > a <= 5:
#     print("II")
# else:
#     print("III")


# 4.59. Дано целое число n (1 <= n <= 99), определяющее возраст человека (в годах). Для этого числа напечатать фразу "мне n лет", учитывая, что при некоторых значениях n слово "лет" надо заменить на слово "год" или "года". 

# age = 11

# if age % 10 == 1 and age != 11:
#     print(f"Чуловеку {age} год")
# elif age % 10 == 2 or age % 10 == 3 or age % 10 == 4:
#     print(f"человеку {age} года")
# elif age >= 11 and age <= 14 :
#     print(f"человеку {age} лет")


# #==========================================================
# Дано двузначное число Определить
# 1) Является ли сумма его цифр двузначным числом
# 2) Больше ли числа а сумма его цифр

number = int(input("Введите дву значное число: "))
if 10<= (number % 10) + (number // 10) <= 99:
    print("является")
          
if (number % 10) + (number // 10) >= 10 and (number % 10) + (number // 10) <= 99:
    print("является")
    