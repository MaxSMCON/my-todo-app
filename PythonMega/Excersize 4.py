

file = open('essay.txt', 'r')

text = file.read()

print(text.title())

n_char = len(text)

print("number of characters: ", n_char)

user_input = input("Add a new member: ")
user_input.strip()

mem = open('members.txt', 'r')
existing_members = mem.readlines()
# print(text)
mem.close()


existing_members.append(user_input +"\n")

mem = open('members.txt', 'w')

existing_members = mem.writelines(existing_members)
file.close()


#  Exercse 4

texts = ["Hello There", "Hello Hello", "Hello Again"]

files = ['1.txt', '2.txt', '3.txt']

for text, file in zip(texts, files):
    file = open(file, 'w')
    file.write(text)
    print(text)

file = open("data.txt", 'w')

file.writelines("100.12 \n")
file.writelines("111.23 \n")

file.close()


file = open("data.txt", 'r')
file.write("100.12")
file.close()