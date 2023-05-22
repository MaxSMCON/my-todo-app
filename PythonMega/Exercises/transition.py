
temp_min = 0
temp_max = 100

def phase_state(user_input):
    try:
        user_input = user_input.strip()
        user_input= float(user_input)
        if user_input <= temp_min:
            return 'solid'
        elif temp_min < user_input < temp_max:
            return 'liguid'
        else:
            return 'gas'
    except ValueError:
        print("Your command isn't valid")



