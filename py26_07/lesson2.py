# Классы в Python

'''
Классом в Python считается именованный участок кода, начинающийся со слова class

class ClassName(object):
    """docstring for ."""

    def __init__(self, arg):
        super(, self).__init__()
        self.arg = arg


1. class - управляющая конструкция, объявляющая интерпретатору точку начала описания класса.
2. ClassName - имя класса, с помощью которого он будет вызываться по всей программе.
3. (object) | необязательный параметр - это аргументы, необходимые для КОНСТРУИРОВАНИЯ
экземпляра класса, или объект(-ы) наследования, на основе которых создается новый класс.
4. def __init__(self) | необязательный параметр - функция ИНИЦИАЛИЗАЦИИ экземпляра класса.
Эта функция срабатывает в момент, когда объект уже создан и его надо дополнительно расширить
данными.
5. self - указатель класса на самого себя. (cls)
'''

# string = int("10")
# 1. class int:...
# 2. int.__new__(cls, "10")
# 3. string <- return int.__new__(cls, "10")

# cls - базовый прототип ЛЮБОГО проектируемого класса в Python

# ------------------------------------------------------------------------------

class BinNumber:
    # Инициализация объекта, с передачей в него числа, в качестве аргумента
    def __init__(self, number): # *args, **kwargs - любой набор любых аргументов
        # Создает в объекте поле number и записывает в него число, полученное в процессе
        # инициализации в двоичном виде
        self.number = bin(number)

    # Перегрузка (или override) методов
    def __repr__(self):
        return f"{self.number}"

# создайте класс HexNumber, который будет принимать на вход число в десятичном виде,
# сохранять это число в поле number уже в шеснадцатиричном формате, а при вызове
# функции print() на экран будет выводится строка "Your hex translation is: {number}"

# class HexNumber:
#     def __init__(self, number): # *args, **kwargs - любой набор любых аргументов
#         # Создает в объекте поле number и записывает в него число, полученное в процессе
#         # инициализации в двоичном виде
#         self.number = hex(number)
#
#     # Перегрузка (или override) методов
#     def __repr__(self):
#         return f"Your hex translation is: {self.number}"

class HexNumber(BinNumber):
    def __new__(cls, number):
        instance = object.__new__(cls)
        instance.number = hex(number)
        return instance

    def __init__(self, number):
        pass

    def __repr__(self):
        return f"{self.number}"

num = BinNumber(100) # BinNumber(100) -> __init__(100) -> self.number = 0b10010
hnum = HexNumber(100)
# num.__init__(1200) # num.__init__(1200) -> self.number = 0b10010110000
print(num) # print(num) -> print(num.__repr__()) -> num.__repr__() >> std::cout
print(hnum)

# ДЗ
# создайте класс DecNumber, который будет принимать на вход число в десятичном виде,
# сохранять это число в поле number уже в восьмиричном формате, а при вызове
# функции print() на экран будет выводится строка "Your dec translation is: {number}"
