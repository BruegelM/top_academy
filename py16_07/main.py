# классы в pythone считается именованный участок кода начинающийся с ключевого слова class

# 1. class - управляющая конструкция объявляющая интерпретатору точку начала описания класса
# 2. classname - имя класса, с помощью которого он будет вызываться по всей программе
# 3. (object) |необязательный элемент| - который необходим для конструирования экземпляра класса иои объекты наследования на основе которых создается новый класс
# 4. def __init__(self, param1, param2, ...) |необязательный элемент| - метод инициализации класса, который вызывается когда объект уже создан и его надо дополнительно надо расширить данными
# 5. self - ссылка на текущий объект класса


# class BinNumber:
#     def __init__(self, number): # *args, **kwargs - любой набор любых аргументов
#         self.number = bin(number)
# перезагрузка override методов
#     def __repr__(self):
#         return f"{self.number}"


# num = BinNumber(100)
# num.__init__(1200)
# print(num)

#========================================================================

#создать класс BinNumber которое будет принимать число вдесятичном виде, потом сохранять это число вшестнадцатиричном виде а при вызове функции print на экран будет выводиться текст "Your Hex translation is: (number)"

class HexNumber:
    def __init__(self, number):
        self.number = hex(number)
    
hex = HexNumber(9923423)
print(f"Your Hex translation is: {hex.number}")


#ДЗ:

class DecNumber:
    def __init__(self, number):
        # Сохраняем число в восьмеричном формате
        self.number = oct(number)

    def __repr__(self):
        return f"Your dec translation is: {self.number}"

# Пример использования:
dnum = DecNumber(100)
print(dnum)  # Output: Your dec translation is: 0o144
