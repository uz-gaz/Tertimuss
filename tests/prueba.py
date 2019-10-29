import math
import random


def divisor_generator(n):
    large_divisors = []
    for i in range(1, int(math.sqrt(n) + 1)):
        if n % i == 0:
            yield int(i)
            if i * i != n:
                large_divisors.append(n / i)
    for divisor in reversed(large_divisors):
        yield int(divisor)


if __name__ == '__main__':
    min_to_use = 2
    max_to_use = 13
    selected = [i for i in divisor_generator(24) if min_to_use <= i <= max_to_use]
    print(random.choices(selected, k=14))
