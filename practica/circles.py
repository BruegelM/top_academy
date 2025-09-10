#range(start, end-1, step)
#num = range(1,10) - 1,2,3,4,5,6,7,8,9
# range(8) = range(0, 8) - 0,1,2,3,4,5,6,7
# range(1,10,2) - 1,3,5,7,9
# range(1,10+1) - до 11
# range(10,1,-1) - 9,8,7,6,5,4,3,2
# range (10,2) - нельзя

# Циклы с параметром for in

# for number in range (1,10+1):
#     res = number + 1
#     print(res)

# for number in range (1,10+1):
#     if number %2 == 0:
#         print(f"{number} четное")

# for _ in range (10):
#     print(20, end=" ")

# for i in range (20,35+1):
#     print(i)


# b = 30
# for num in range(10,b+1):
#     print(num**2)

# for i in range (10,25+1):
#     print(i, i+0.4)

for i in range(1,10,1):
    print(i*7)

for i in range(1,10,1):
    print(f"{i} x 9 = {i*9}")

b = input("Введи число: ")
for i in range(1,10,1):
    print(f"{i} x {b} = {i*b}")