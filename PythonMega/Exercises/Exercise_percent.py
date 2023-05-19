
try:
    user_total_input = int(input('Enter total value: '))
    user_value_input = int(input('Enter value: '))

    # if user_total_input.isdigit() and user_value_input.isdigit():
    print(f"That is {user_value_input / user_total_input :.2}%")
except ValueError:
    print('You need to enter a number. Run program agian')

except ZeroDivisionError:
    print('Your total value cannot be zero.')

