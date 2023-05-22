import random

user_lower = int(input("Enter the lower bound: "))
user_upper = int(input("Enter the upper bound: "))

result = random.randint(user_lower, user_upper)

print(result)