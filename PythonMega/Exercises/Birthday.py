
user_year_birth = input("Enter year you were born: ")

def your_age(user_year_birth, current_year = 2023):
    age = current_year - float(user_year_birth)
    return age

age = your_age(user_year_birth)

print(f'Your age is {age} years')


def calculate_time(h, g=9.80665):
    t = (2 * h / g) ** 0.5
    return t


time = calculate_time(100)
print(time)