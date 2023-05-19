feet_inches = input('Enter feet and inches: ')

def parse(feet_inches):
    parts= feet_inches.split(" ")
    feet = float(parts[0])
    inches = float(parts[1])
    return {"feet":feet, "inches":inches}
def convert(feet, inches):
    meters = feet * 0.3048 + inches * 0.0254
    # return f"{feet} feet and {inches} is equal to {meters:.2f} meters"
    return meters


parsed = parse(feet_inches)
result = convert(parsed['feet'], parsed['inches'])
print(f"{parsed['feet']} feet and {parsed['inches']} inches is equal to {result}")

if result < 1:
    print('Kid is too small')
else:
    print("Kid can use the slide")

# liters

liters = input("enter liters: ")

def convert_volume(liters):
    cubic_meter = float(liters) / 1000
    return cubic_meter

cubic_meters = convert_volume(liters)
print(f'{cubic_meters} cubic meters')

password = input('Enter password: ')

def check_pasword(password_local):
    result = {}
    if len(password_local) > 7:
        result["length"] = True
    else:
        result['length'] = False
    digit = False
    uppercase = False
    for passw in password_local:
        if passw.isupper():
            uppercase = True
        if passw.isdigit():
            digit = True

    result['digit'] = digit
    result['uppescase'] = uppercase

    if all(result.values()):
        return 'strong password'
    else:
        return 'weak password'

# print(check_pasword(password))


def speed(distance, time):
    return float(distance) / float(time)


print(speed(200, 4))