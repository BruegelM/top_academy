def bubbleSort(numbers: list[int])->list[int]:
    # Получаем размер массива
    n = len(numbers)
    # запускаем цикл for по всей длинне массива
    for i in range(n-1):
        swapped = False
        for j in range(0, n-1-i):
            if numbers[j] > numbers[j+1]:
                # оппарно переставляем значения местами если текущий элемент больше предыдущего
                numbers[j], numbers[j+1] = numbers[j+1], numbers[j]
                swapped = True
        if not swapped:
            break
    return(numbers)

numbers = [9, 2, 7, 4, 8, 5, 1, 3, 0, 23, 32, 34, 45]
sortedNumbers = bubbleSort(numbers)
print(sortedNumbers)