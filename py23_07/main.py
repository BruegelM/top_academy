"""
Супер класс пользователя от которого будут наследоваться все остальные реализации

user,check_role(self,role) - функция принимающая в себя число и являющаяся идентификатором роли и сравнивает полученную росль с ролью (self.role) объекта. Если роли совпадают - возвращает true, если нет False
""" 

"""Пример использования наследования"""
class User:
    def __init__(self, id_: int, priveleges: list, role: int, description: str)-> None:
        self.__id = id_
        self.__priveleges = priveleges
        self.__role = role
        self.__description = description

    def check_role(self, role: int)-> bool:
        return self.__role == role
        
    def get_priveleges(self) -> list:
        return self.__priveleges
    
    def get_id(self) -> int:
        return self.__id
    
    def get_profile(self) -> str:
        pass
    
class Profile(User):
    def __init__(self, id_: int, priveleges: list, role: int, description: str, username: str, password: str, name: str)-> None:
        super().__init__(id_, priveleges, role, description)
        self.__username = username
        self.__password = password
        self.__name = name
    def __repr__(self):
        return f"User: {super().get_priveleges()}, username: {self.__username}, name: {self.__name}"




priveleges = ["high", "build", "create", "delete", "put", "update"]
user = User(1, priveleges, 0, "Ёбаный админ в хате!")
profile = Profile(2, priveleges, 0, "Это аккант созданный из профиля", "Тварь дрожащая - detected", "secure_password", "Иван Иванов")

print(f"Object: {user}, id: {user.get_id()}")
print(f"Object: {profile}, id: {profile.get_id()}")

"""Пример использования полиморфизма"""

import abc

class Animal(abc.ABC):
    def __init__(self, type_: str):
        self.__type = type_

    
    @abc.abstractclassmethod
    def say(self):
        pass

class Cat(Animal):
    def say(self):
        print("Meow")

cat = Cat('cat')
cat.say()