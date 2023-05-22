import webbrowser

user_input = input("Enater saerch: ").replace(" ", "+")

webbrowser.open("https://www.google.com/search?q=" +user_input)

