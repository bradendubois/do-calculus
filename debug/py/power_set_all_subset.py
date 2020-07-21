from util.helpers.PowerSet import power_set

y = {1, 2, 3, 4}

subsets = [s for s in set(power_set(y, False)) if len(s) != len(y)]

print(subsets)
