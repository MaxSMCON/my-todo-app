import itertools

# Define the values you want to use for the combination
values = [10, 20, 30, 386.8, 852.4, 878.5, 929.8, 955.2, 955.2, 957.6, 957.6, 985.2, 995, 995, 1000.4, 1010.8, 1016, 1034, 1034.6, 1039.2, 1076, 1102.2, 1115.8, 1133, 1152.5]

# Define the target sum you want to achieve
target_sum = 3107.2

# Generate all combinations of length 3 from the values
combinations = itertools.combinations(values, 4)

# Iterate through the combinations to find the one that adds up to the target sum
for combo in combinations:
    if sum(combo) == target_sum:
        print("Combination found:", combo)
        break
else:
    print("No combination found that adds up to the target sum.")

# import itertools
#
# values = [386.8, 852.4, 878.5, 929.8, 955.2, 955.2, 957.6, 957.6, 985.2, 995, 995, 1000.4, 1010.8, 1016, 1034, 1034.6, 1039.2, 1076, 1102.2, 1115.8, 1133, 1152.5]
# target_sum = 3107.6
#
# for combination in itertools.combinations(values, 3):
#     if sum(combination) == target_sum:
#         print("A combination of 3 elements that add up to the target sum is:", combination)
