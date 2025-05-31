import random

def fixed_sum_random(n, total):
    nums = [random.random() for _ in range(n)]
    scale = total / sum(nums)
    return [x * scale for x in nums]
