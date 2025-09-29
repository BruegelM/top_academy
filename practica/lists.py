
# a = iter(range(4))
# print(next(a))
# print(next(a))

# for i in iter(range(4)):
#     print(i)


# lst = [1,2,3,4,5,] # изменяемый это список
# print(lst)
# tuples = (1,2,3,4) # неизменяемый это кортеж

# lst = [1,2,3,4,5,] # упорядоченность это возможность использовать индексы в структуре данных
# print(lst[3])
# tuples = (1,2,3,4) # 
# упорядоченным является кортежи и строки
# множество - неупорядоченное
# словари - 50/50 ключ значение


# посчитать сумму цифр в числе 123234567869
# summa = 0
# for element in "123234567869":
#     summa += int(element)
# print(summa)


#==============================================================================
#append()

# append()
# 1. Напишите программу, которая создает список покупок. Программа должна запрашивать у пользователя элементы до тех пор, пока он не введет "стоп". После этого выведите итоговый список покупок.
# 2. Создайте список `students` и добавьте в него имена студентов, вводимые пользователем. Когда пользователь введет "конец", программа должна вывести список всех студентов.
# 3. Напишите программу, которая создает список из 10 случайных чисел, добавляя каждое число к списку по одному.


# def shop_market(tov):
#     while True:
#         element = input("Введите любой товар: ")
#         if element == "стоп":
#             break

#         tov.append(element)


# def main():
#     tovars = []
#     shop_market(tovars)
#     print(tovars)


# main()

# def students_list(std):
#     while True:
#         stud = input("Введите фамилию студента: ")
#         if stud == "стоп":
#             break
#         std.append(stud)

# def main():
#     students = []
#     students_list(students)
#     print(students)

# main()
# from random import randint

# def list(lst):
#     for list in range(10):
#         list = lst.append(randint(0,10))

# def main():
#     lst = []
#     list(lst)
#     print(lst)

# main()

#  extend()
# 1. Напишите программу, которая объединяет списки сотрудников из двух отделов `department1` и `department2` в один общий список `all_employees`.
# 2. Создайте список из месяцев года. Пользователь вводит имена дополнительных месяцев (например, для особых календарей), и программа добавляет их к списку.
# 3. У вас есть список чисел `a = [1, 2, 3]` и список чисел `b = [4, 5, 6]`. Создайте программу, которая объединяет эти два списка и выводит результат.

# def all_employees(dept1, dept2, dept3):
#     while True:
#         dept1 = int(input("Введите список фамилий для Департамента №1: "))
#         if dept1 == "стоп":
#             break
#         else: dept3.extend(dept1)
#     while True:
#         dept2 = int(input("Введите список фамилий для Департамента №2: "))
#         if dept2 == "стоп":
#             break
#         else: dept3.extend(dept2)

#         return(dept3)

# def main():
#     department1 = []
#     department2 = []
#     department3 = []
#     all_employees(department1, department2, department3)
#     print(department3)

# main()


#==============================================================================
# ЗАДАЧА 11.15
# 11.15. Дан массив. Составить программу: 
#            а) расчета квадратного корня из любого элемента массива; 
#            б) расчета среднего арифметического двух любых элементов массива. 


# from random import randint
# from math import sqrt

# lst = []

# def input_lst():
#     size = int(input("Введите сколько элементов массива вы хотите: "))

#     for _ in range(size):
#         lst.append(randint(-100,100))

# def output_lst():
#     bar = "==" * len(lst)
#     print("====ВАШ СПИСОК====")
#     print(f"{bar*2}\n{lst}\n{bar*2}")

# def calculate_element_lst():
#     element = int(input("Введите какой элемент ихз массива вы хотите sqrt: "))
#     output_lst()

#     if element not in lst:
#         print(f"Такого элемента {element} нет")
#         return #None, None
    
#     if element < 0:
#         print(f"Элемент {element} является отрицательным")
#         return #None, None
    
#     return (element, sqrt(element))

# def average_calculate_elementv2():
#     output_lst()

#     elements = []
#     while True:
#         element = input("Введите элемент из массива (или стоп): ")
#         if element == "стоп":
#             break
#         element = int(element)
#         if element not in lst:
#             continue
#         elements.append(element)

#     average = sum(lst) / len(elements)
#     return average

# def main():
#     input_lst()
#     output_lst()

#     # element, res_a = calculate_element_lst()
#     # if element:
#     #     print(f"Квадратный корень из {element} = {res_a}")
#     res_a = calculate_element_lst()
#     res_a3 = average_calculate_elementv2()
#     if res_a:
#         print(f"Квадратный корень из {res_a[0]} = {res_a[1]}")
#     print(res_a3)

# main()

#==============================================================================
# ЗАДАЧА 11.17
# 11.17. Дан массив. Все его элементы: 
#            а) увеличить в 2 раза; 
#           б) уменьшить на число А; 
#           в) разделить на первый элемент. 



# from random import randint
# from math import sqrt

# lst = []


# def input_lst():
#     size = int(input("Введите сколько элементов массива вы хотите: "))

#     for _ in range(size):
#         lst.append(randint(-100,100))

# def output_lst():
#     bar = "==" * len(lst)
#     print("====ВАШ СПИСОК====")
#     print(f"{bar*2}\n{lst}\n{bar*2}")

# def all_lst_muliply_on_2():
#     #lst_copy = lst.copy()
    
#     lst_res = []
#     for elem in lst:
#         lst_res.append(elem * 2)


#     lst_copy = lst.copy()
#     for i in range(len(lst_copy)): # дут фактически создаст список индексов в range
#         lst_copy[i] = lst_copy[i] * 2

#     print(f"первый вариант: {lst_res}")
#     print(f"ворой вариант: {lst_copy}")

# def divisor_lst_element():
#     lst_copy = lst.copy()

#     one_elem = lst_copy[0]

#     for i in range(len(lst_copy)):
#         lst_copy[i] = lst_copy[i] / one_elem

#     print(f"все разделили на {one_elem}: {lst_copy}")

# def main():
#     input_lst()
#     output_lst()
#     all_lst_muliply_on_2()
#     divisor_lst_element()

# main()

#======================================================================================
#Задача 11.19
# 11.19. Определить: 
#           а) сумму всех элементов массива; 
#           б) произведение всех элементов массива; 
#           в) сумму квадратов всех элементов массива; 
#           г) сумму шести первых элементов массива; 
#           д) сумму элементов массива с k1-го по k2-й (значения k1 и k2 вводятся с клавиатуры; k2 > k1); 
#           е) среднее арифметическое всех элементов массива; ж) среднее арифметическое элементов массива с s1-го по s2-й (значения s1 и s2 вводятся с клавиатуры; s2 > s1).


# from random import randint
# from math import sqrt

# lst = []
# def input_lst():
#     size = int(input("Введите сколько элементов массива вы хотите: "))

#     for _ in range(size):
#         lst.append(randint(-100,100))

# def output_lst():
#     bar = "==" * len(lst)
#     print("====ВАШ СПИСОК====")
#     print(f"{bar*2}\n{lst}\n{bar*2}")

# def calculate_slice_lst():
#     output_lst()
#     k1 = int(input("введите номер первого элемента: "))
#     k2 = int(input("введите номер второго элемента: "))

#     if k2 < k1:
#         return

#     summa =0
#     for i in range(k1-1,k2):
#        summa += lst[i]

#     print(f"сумма равна {summa}")


# def main():
#     input_lst()
#     output_lst()
#     calculate_slice_lst()

# main()

#======================================================================================
# 11.16. Дан массив целых чисел. Выяснить: 
#            а) является ли s-й элемент массива положительным числом; 
#            б) является ли k-й элемент массива четным числом; 
#            в) какой элемент массива больше: k-й или s-й. 
 

# from random import randint
# from math import sqrt

# lst = []
# def input_lst():
#     size = int(input("Введите сколько элементов массива вы хотите: "))

#     for _ in range(size):
#         lst.append(randint(-100,100))

# def output_lst():
#     bar = "==" * len(lst)
#     print("====ВАШ СПИСОК====")
#     print(f"{bar*2}\n{lst}\n{bar*2}")


# def poloj(s):
#     if lst[s-1] > 0:
#         print(True)
#     else:
#         print(None)

# def chet(k):
#     if lst[k-1] % 2 == 0:
#         print(True)
#     else:
#         print(None)

# def bolsh(s,k,lst):
#     if lst[k-1] > lst[s-1]:
#         print(f"{k} - больше") 
#     else:
#         print(f"{s} - больше") 

#     return(bolsh,chet,poloj)

# def main():
#     input_lst()
#     output_lst()
#     k = int(input("Введите номер K элемента: "))
#     s = int(input("Введите номер S элемента: "))
#     bolsh(s,k,lst)
#     chet(k)
#     poloj(s)

# main()

#======================================================================================
# 11.36. Дан массив. Напечатать: 
#           а) все неотрицательные элементы; 
#           б) все элементы, не превышающие число 100. 

from random import randint

lst = []
def input_lst():
    size = int(input("Введите сколько элементов массива вы хотите: "))

    for _ in range(size):
        lst.append(randint(-100,100))

def output_lst():
    bar = "==" * len(lst)
    print("====ВАШ СПИСОК====")
    print(f"{bar*2}\n{lst}\n{bar*2}")

def minus_lst(lst):
    size = len(lst)
    lst2 = [0]
    element = [0]
    if element in range(0,size) > 0:
        lst2.append(element)
        continue
        
    print(lst)

def main():
    input_lst()
    output_lst()
    minus_lst(lst)
    #non_100_lst(lst)

main()