from typing import List


# Taken from https://stackoverflow.com/questions/45323619/python-greatest-common-divisor-gcd-for-floats-preferably-in-numpy
def __float_gcd(a: float, b: float, rtol: float = 1e-05, atol: float = 1e-08) -> float:
    t = min(abs(a), abs(b))
    while abs(b) > rtol * t + atol:
        a, b = b, a % b
    return a


def float_gcd(numbers: List[float], rtol=1e-05, atol=1e-08) -> float:
    if len(numbers) > 0:
        gcd_accumulated = numbers[0]
        for number in numbers[1:]:
            gcd_accumulated = __float_gcd(gcd_accumulated, number, rtol, atol)
        return gcd_accumulated
    else:
        return 1
