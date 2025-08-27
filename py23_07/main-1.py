'''
    Фукнция - это обособленный участок кода, выполняющий описанный внутри функции набор команд,
    в качестве результата предоставляющий результат выполнения команд. Функция выполняет одну
    конкретную задачу.

    Функция в Python характеризуется следующими элементами:
        - ключевая лексема 'def' объявляет последующий код как функцию
        - имя функции, например 'foo', 'bar' и т.д., объявляет псевдоним для вызова функции
        - набор аргументов, заключенный в круглые скобки, например '(a, b, c)'

    Описание функции выглядит следующим образом:
        def foo(a, b, c):
            instruction 1
            instruction 2
            cycle 1:
                cycle instruction 1
                ...
            if cond1:
                instruction 1
                ...
            else:
                ...

    Функции в Python могут быть возвратными и не возвратными (returnable)
    Чтобы функция возвращала какие-либо значения после своего выполнения, в функции должен
    присутствовать оператор return

    def foo1(a, b, c):
        a + b + c # <- возвращает None

    def foo2(a, b, c):
        return a + b + c # <- возвращает сумму аргументов функции
'''

def getOddsBetween(a: int, b: int)->list:
    odds = []
    for number in range(a, b+1):
        if number % 2 != 0:
            odds.append(number)
    return odds

def findMax(a: int, b: int, c: int)->int:
    max_int = a
    if max_int < b:
        max_int = b
    if max_int < c:
        max_int = c
    return max_int

def findMin(a: int, b: int, c: int)->int:
    min_int = a
    if min_int > b:
        min_int = b
    if min_int > c:
        min_int = c
    return min_int

def luckyNumber(number: int)->bool:
    numbers = []
    for i in range(6):
        numbers.append(number%10)
        number = number // 10
    numbers.reverse()
    return sum(numbers[0:3]) == sum(numbers[3:6])

def bubbleSort(numbers: list[int])->list[int]:
    # Получаем размер переданного списка
    n = len(numbers)
    # Запускаем цикл for по всей длине массива
    for i in range(n-1):
        swapped = False
        for j in range(0, n-1-i):
            if numbers[j] > numbers[j+1]:
                # Попарно переставляем значения местами, если текущий элемент больше
                # чем последующий
                numbers[j], numbers[j+1] = numbers[j+1], numbers[j]
                swapped = True
        if not swapped:
            break
    return numbers

print(bubbleSort([1256,1,7,12,56,100,1,16,7,8,0,23,11]))
        
# ДЗ!!!
# Отредактировать bubbleSort таким образом, чтобы алгоритм сортировал от большего к меньшему

def bubbleSort(numbers: list[int]) -> list[int]:
    n = len(numbers)
    for i in range(n-1):
        swapped = False
        for j in range(0, n-1-i):
            # Меняем знак сравнения на < для сортировки по убыванию
            if numbers[j] < numbers[j+1]:
                numbers[j], numbers[j+1] = numbers[j+1], numbers[j]
                swapped = True
        if not swapped:
            break
    return numbers

print(bubbleSort([1256,1,7,12,56,100,1,16,7,8,0,23,11]))
