


user_country = input('Input the country you are from? ')
user_country = user_country.strip()
# user_country = user_country.capitalize()
match user_country:
    case 'USA':
        print('Hello')
    case 'India':
        print('Namaste')
    case 'Germany':
        print('Hallo')
    case _:
        print("Well I don't know what to say" )

