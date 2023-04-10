filenames  = ['1.doc', '1.report', '1.presentation']

filenames = [filename.replace('.','-') + '.txt' for filename in filenames]

print(filenames)

new = [i for i in ['a', 'b', 'c']]
print(new)

names = ["john smith", "jay santi", "eva kuki"]

names = [name.title() for name in names]

print(names)


usernames = ["john 1990", "alberta1970", "magnola2000"]

usernames = [len(username) for username in usernames]

print(usernames)

user_entries = ['10', '19.1', '20']
user_entries = [float(user_entrie) for user_entrie in user_entries]
print(sum(user_entries))
print(user_entries)

temperatures = [10, 12, 14]

file = open("file.txt", 'w')

temperatures = [str(i)+'\n' for i in temperatures]
file.writelines(temperatures)


numbers = [10.1, 12.3, 14.7]
numbers = [int(number) for number in numbers]
print(numbers)


