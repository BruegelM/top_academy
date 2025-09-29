# Надо пройти еще map, filter reduece и что-то еще.  функции высшего порядка - вызывают или возвращают результат выполнения других функций

lst = [

    [1,2,3],
    [4,5,6],
    [7,8,9]
]

for i in range(len(lst)):
    for j in range(len(lst)):
        if lst[i][j] % 2 == 0:
            print(lst[i][j])