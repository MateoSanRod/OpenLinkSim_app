
def check_zeros(list1, list2):
    if len(list1) != len(list2):
        raise ValueError("Input lists must have the same length.")
    return any(x == 0 and y == 0 for x, y in zip(list1, list2))