#!/usr/bin/python3
def weight_average(my_list):
    total_weighted_sum = 0
    total_weights = 0

    for value, weight in my_list:
        total_weighted_sum += value * weight
        total_weights += weight

    if total_weights == 0:
        return 0
    else:
        return total_weighted_sum / total_weights
