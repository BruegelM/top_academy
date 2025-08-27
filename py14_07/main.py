# Задание 1
number = int(input())
if number %7 == 0:
        print("Number is multiplied 7")
else:
        print("Number is not multiplied 7")

# Задание 2
if number %2 == 0:
        print("Even number")
else:
        print("Odd number")

# Задание 3
number1 = int(input())
number2 = int(input())
if number1 > number2:
        print("Number1 is bigger than number2")
else:
        print("Number2 is bigger than number1")

# Задание 4
number1 = int(input())
number2 = int(input())
minimum = min(number1, number2)
print("Minimum number is", minimum)

# Задание 5
number1 = float(input())
number2 = float(input())
number3 = float(input())
operation = input()
if operation == "+":
        result = number1 + number2 + number3
        print("Result is", result)
elif operation == "-":
        result = number1 - number2 - number3
        print("Result is", result)
elif operation == "*":
        result = number1 * number2 * number3
        print("Result is", result)
elif operation == "avg":
        result = (number1 + number2 + number3)/3
        print("Result is", result)