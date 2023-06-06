FILEPATH = 'todos.txt'

def get_todos(filepath=FILEPATH):
    """read lines from provided file"""
    with open(filepath, 'r') as file_local:
        todos_local = file_local.readlines()
    return todos_local

# print(help(get_todos))
def write_todos(todos_arg, filepath=FILEPATH ):
    """ Write the to do items list in the text file"""
    with open(filepath, 'w') as file:
        file.writelines(todos_arg)

if __name__ =="__main__":
    print("Hello")
    print(get_todos())