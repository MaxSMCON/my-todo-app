
# from functions import get_todos, write_todos
import functions
import time

now = time.strftime("%b %d, %Y, %H:%M:%S")
print("It is", now)


while True:
    user_action = input('Type add, show, edit, complete or exit: ')
    user_action = user_action.strip()

    if user_action.startswith("add") or user_action.startswith('new'):
        todo = user_action[4:] + '\n'

        todos = functions.get_todos()

        todos.append(todo)

        functions.write_todos(todos)

    elif user_action.startswith('show'):
        todos = functions.get_todos()

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

            todos = functions.get_todos()

            # print("Here is todos: ", todos)
            new_todo = input("Enter new todo: ")
            todos[number] = new_todo + '\n'
            # print("Here is the new todos: ", todos)

            functions.write_todos(todos)

        except ValueError:
            print("Your command isn't valid")
            continue

        # print(existiing_todo)
    elif user_action.startswith('complete'):
        try:
            number = int(user_action[9:])

            todos = functions.get_todos()

            index = number - 1
            todo_to_remove = todos[index].strip('\n')
            todos.pop(index)

            functions.write_todos(todos)

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
