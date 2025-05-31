import random

def fixed_sum_random(n, total):
    nums = [random.randint(0,10000) for _ in range(n)]
    scale = total / sum(nums)
    times = [x * scale for x in nums]
    times = [int(round(i, 0)) for i in times]
    remaining = total - sum(times) 
    step = 1 if remaining > 0 else -1
    while remaining != 0:
        i = random.randint(0, n - 1)
        if times[i] + step >= 0:
            times[i] += step
            remaining -= step
    return times


 # check if there are corrections to be done
