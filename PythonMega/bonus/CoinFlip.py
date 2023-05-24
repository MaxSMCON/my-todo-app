file_path = "../journal/CoinFlip.txt"
while True:
    with open(file_path, "r") as file:

        coin_flips = file.readlines()

    coin_flip = input("Throw the coin and enter head or tail here: ?").strip() + "\n"

    match coin_flip:
        case 'head\n' | 'tail\n':

            with open("../journal/CoinFlip.txt", "r") as file:
                coin_flips = file.readlines()
            coin_flips.append(coin_flip)

            with open("../journal/CoinFlip.txt", "w") as file:
                file.writelines(coin_flips)
            nr_heads = coin_flips.count("head\n")
            percentage = nr_heads / len(coin_flips) * 100

            print(f"Heads: {percentage:.2f}%")

        case "exit\n":
            print('Bye Bye')
            break

        case _:
            print("please enter head or tail")