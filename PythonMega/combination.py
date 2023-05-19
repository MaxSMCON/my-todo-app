import itertools

# Define the values you want to use for the combination
import itertools

# Define the values you want to use for the combination
values = [
    875.4
, 979.5
, 1012
, 551.5
, 871
, 933.6
, 963
, 987.6
, 1058.2
, 1068
, 1042.4
, 1029.2
, 1022
, 1032.8
, 293
, 634.8
, 479
, 972
, 954
, 139.5
, 945
, 340
, 999.2
, 1036.4
, 959
, 1031.6
, 1008.8
, 983
, 994.2
, 967
, 1020.4
, 1086.6
, 466
, 960.2
, 1061.6
, 1004.4
, 997
, 905.2
, 968.2
, 1022.8
, 966.4
, 516.5

]

Number_of_combinations = 5
# Define the target sum you ant to achieve
target_sum = 3145.6

# Generate all combinations of length 3 from the values
combinations = itertools.combinations(values, Number_of_combinations)

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
