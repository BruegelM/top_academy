"""
Функция - это обособленный участок кода, выполняющий описанный внутри функции набор комагд. в качестве результата продоставляется результат выполнения команды. Функция выполняет одну конкретную задачу. 

Функция в python - характеризуется следующими элементами
- ключевая лексема def - объявляет последующий код как функцию
- название функции - например 'foo', 'bar' и т.д. объявляет псевдоним для вызова функции
- список аргументов - заключенный в круглые скобки, например (a, b, c) 

Описание функции выглядит следующим образом:
def foo(a, b, c):
    instruction 1
    instruction 2
    instruction 3
    cycle 1:
        cycle instruction 1
        ...
    if cond1:
        instruction 1
        ...
    elif cond2:
        instruction 2
        ...
    else:
        instruction 3
        ...
Функции в Python могут быть возвратными и невозвратными (returnable)
Чтобы функция возвращала результат, необходимо использовать ключевое слово return.

def foo(a, b, c):
    return a + b + c <- возвращает результат
    a + b + c <- возвращает None


"""

# def getOddsBetween(a: int, b: int) -> list:
#     odds = []
#     for number in range(a, b+1):
#         if number % 2 != 0:
#             odds.append(number)
#     return odds

# result = getOddsBetween(1, 91)
# print(result)

# def maximumNumber(a: int, b: int, c: int, d: int) -> int:
#     max_int = a
#     if b > max_int:
#         max_int = b
#     if c > max_int:
#         max_int = c
#     if d > max_int:
#         max_int = d
#     return max_int

# result = maximumNumber(1, 91, 5, 456)
# print(result)

# def minimumNumber(a: int, b: int, c: int, d: int) -> int:
#     min_int = a
#     if b < min_int:
#         min_int = b
#     if c < min_int:
#         min_int = c
#     if d < min_int:
#         min_int = d
#     return min_int

# result = minimumNumber(1, 91, 5, 456)
# print(result)

def luckyNum(number: str)->bool:
    numbers = []
    for i in range(6):
        numbers.append(number%10)
        number = number // 10
        #numbers.reverse()
        #return numbers[0]+numbers[1]+numbers[2] ==      numbers[3]+numbers[4]+numbers[5]
    return sum(numbers[0:3]) == sum(numbers[3:6])

result = luckyNum(123420)
print(result)
