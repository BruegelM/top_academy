# # найти количество десятков
# def sum_number(num1, num2):
#     sum = num1 + num2
#     return sum

# def search_digit(num):
#     digit = num % 10
#     return digit

# def search_tens(num):
#     tens = num // 10 #"pass" or "... - одно и тоже
#     return tens

# def main ():
#     number = int(input("Введите двузначное число: "))
#     result = search_tens(number)
#     res = search_digit(number)
#     res2 = sum_number(result,res)
#     print(res2)

# main()

# def summa_chisel(number):
#     return (number % 10) + (number // 10)

# def summa_kratna_a(number):
#     a = int(input("Введите а: "))
#     summa = summa_chisel(number)
#     if summa > a:
#         return True
#     return False

# def kra(number):
#     if ((number % 10) + (number // 10)) % 3 == 0:
#         #return "кратно трем сумма его чисел"
#     # print (f"Число {number} кратно трем")
#         return True
#     return False
#     #return None

# def main():
#     number = int(input("Введите двузначное число: "))
#     # kratno3 = kra(number)
#     # print(kratno3)
#     if kra(number):
#         print(f"Число {number} кратно трем")
#     else:
#         print(f"Число {number} некратно трем")
# main()

#Задача: Дано три значения целых числаю определлите какое из них самое большое, маленькое и среднее

#Дано натуральное число. Определите
    # является ли оно четным
    # оканчивается ли оно на 7




# def proverka_nat(num):
#      if num < 0:
#           return True
#      return False

# def cho(num):
#     if num % 2 == 0:
#         print("четное")
#     else:
#         print("нечетное")

# def rav(num):
#     if num %10 == 7:
#         print(f"Число оканчивается на 7")
#     else:
#         print(f"Число не оканчивается на 7")

# def main():
#     number = int(input("Введите уже наконец число: "))
#     if proverka_nat(number):
#             return - 1
#     chotnoe = cho(number)
#     print(chotnoe)
#     ravno_sem = rav(number)
#     print(ravno_sem)

# main()

# WHILE
# summa = 0
# count = 0

# while True:
#     a = int(input("Введите элемент последовательности: "))
    
#     if a % 10 == 0:
#         break
    
#     summa += a
#     count += 1

# print (summa, count)

# for i in range(1,10+1):
#     if i%2==0:
#         continue
#     if i == 11:
#         break
#     result = i**2
#     print(result)
#     print("Привет")

# else:
#     print("все отлично! 11 нет")

#Задача дана последовательность из n вещественных чисел Первое число в последовательности нечетное найти сумму всех идущих подряд в начале последовательности нечетных чисел. Условный оператор не использовать. 

def summa(num):
    flag = True
    summa = 0

    while True:
        num = int(input("Введите последовательность: "))
        if flag:
            if num % 2 == 0:
                break
            flag = False

        if num % 2 == 0:
            break

        summa += num
    
    return summa

def main():
    i = int(input("Введите последовательность: "))
    sum = summa(i)
main ()




