import random

def fixed_sum_random_int(n, total):
    nums = [random.randint(0,10000) for _ in range(n)]
    scale = total / sum(nums)
    nums = [x * scale for x in nums]
    nums = [int(round(i, 0)) for i in nums]
    remaining = total - sum(nums) 
    step = 1 if remaining > 0 else -1
    while remaining != 0:
        i = random.randint(0, n - 1)
        if nums[i] + step >= 0:
            nums[i] += step
            remaining -= step
    return nums


def fixed_sum_random_float(n, total):
    nums = [random.randint(0,10000) for _ in range(n)]
    scale = total / sum(nums)
    nums = [x * scale for x in nums]
    return nums


def uunifast(n, total_utilization):
    """Generate n random utilizations summing to total_utilization."""
    utilizations = []
    sum_u = total_utilization
    for i in range(1, n):
        next_sum = sum_u * random.random() ** (1 / (n - i))
        utilizations.append(sum_u - next_sum)
        sum_u = next_sum
    utilizations.append(sum_u)
    return utilizations