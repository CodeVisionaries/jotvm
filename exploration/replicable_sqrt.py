from decimal import Decimal
from decimal import getcontext
from decimal import ROUND_HALF_EVEN
import time


def sqrt(x):
    number_two = Decimal('2')
    a = x / number_two
    b = x / a  
    last_a = -1
    last_b = -2
    while (a != last_a and b != last_b) and (b != last_a and a != last_b): 
        last_a = a
        last_b = b
        a = (a + b) / number_two 
        b = x / a
    return a


PREC = 100 
value = Decimal(237)

getcontext().prec = PREC
getcontext().rounding = ROUND_HALF_EVEN

s1 = time.time()
res = sqrt(value)
s2 = time.time()
timediff = s2 - s1
print(f'sqrt({value}) = {res}')
print(f'Achieved significant digits: {PREC}')
print(f'Time for computation: {timediff} secs')
