# Программа для работы с 5 числами
print("Введите 5 чисел:")

# Создаем пустой список для хранения чисел
numbers = []

# Запрашиваем 5 чисел у пользователя
for i in range(5):
    while True:
        try:
            num = float(input(f"Введите число {i + 1}: "))
            numbers.append(num)
            break
        except ValueError:
            print("Ошибка! Пожалуйста, введите корректное число.")

print(f"\nВведенные числа: {numbers}")

# Вычисляем и выводим сумму всех чисел
total_sum = sum(numbers)
print(f"Сумма всех чисел: {total_sum}")

# Находим и выводим наибольшее число
max_number = max(numbers)
print(f"Наибольшее число: {max_number}")

# Находим и выводим наименьшее число
min_number = min(numbers)
print(f"Наименьшее число: {min_number}")

# Выводим список в обратном порядке
reversed_numbers = numbers[::-1]
print(f"Список в обратном порядке: {reversed_numbers}")