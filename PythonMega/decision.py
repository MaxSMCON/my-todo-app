#
# todos = []
#

while True:
    user_action = input('Type add, show, edit, complete or exit: ')
    user_action = user_action.strip()

    if user_action.startswith("add") or user_action.startswith('new'):
        todo = user_action[4:] + '\n'
# Context manager
        with open('todos.txt', 'r') as file:
            todos = file.readlines()

        todos.append(todo)

        with open('todos.txt', 'w') as file:
            # file.writelines('\n'.join(todos))
            file.writelines(todos)

    elif user_action.startswith('show'):
        with open('todos.txt', 'r') as file:
            todos = file.readlines()

        for index, item in enumerate(todos):
            # Method 3 susing inside the for loop
            item = item.strip('\n')
            row = f"{index +1}-{item}"
            print(row)
        # print(f"Length is {index + 1}")

    elif user_action.startswith('edit'):
        try:
            number = int(user_action[5:])
            print(number)
            number = number - 1

            with open('todos.txt', 'r') as file:
                todos = file.readlines()
            # print("Here is todos: ", todos)
            new_todo = input("Enter new todo: ")
            todos[number] = new_todo + '\n'
            # print("Here is the new todos: ", todos)
            with open('todos.txt', 'w') as file:
                file.writelines(todos)

        except ValueError:
            print("Your command isn't valid")
            continue

        # print(existiing_todo)
    elif user_action.startswith('complete'):
        try:
            number = int(user_action[9:])

            with open('todos.txt', 'r') as file:
                todos = file.readlines()
            index = number - 1
            todo_to_remove = todos[index].strip('\n')
            todos.pop(index)

            with open('todos.txt', 'w') as file:
                file.writelines(todos)

            message = f"Todo {todo_to_remove} was removed from the list."
            print(message)

        except ValueError:
            print("Your command isn't valid")
            continue

    elif 'exit' in user_action:
        break
    # if _ in user_action:
    #     print('Hey you have enetered unknown command')
    else:
        print('Command is not valid')
print('Bye!')
