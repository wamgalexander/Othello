import numpy as np
import math

def split_by_binary_serach(target, commands):
    split_list = list(target)
    X_index = np.where(np.array(commands)=="X")

    # cut off by "X"
    if len(X_index[0]) > 0:
        valid_commands = list(commands[X_index[0][-1]+1:])
    else:
        valid_commands = list(commands)

    for item in valid_commands:
        index = math.floor(len(split_list)/2)
        if item == "2":
            split_list = split_list[:index]
        elif item == "3":
            split_list = split_list[index:]

        if len(split_list) == 1:
            commands.append("X")
            break

    return split_list

commands = ["3", "2", "X", "2", "3", "X", "2", "2", "2"]
print (split_by_binary_serach([1,2,3,4,5,6,7,8], commands))
print (commands)
