# cache is used as the same S(k,n) may be required to be calculated again

cache:dict[list:float] = {}
def S(k:int,n:int) -> float|int:
    if (k,n) in cache:
        return cache[(k,n)]
    if k == 1:
        return n*(n+1)/2
    val:float = sum([i*S(k-1,i-1) for i in range(k,n+1)])
    cache[(k,n)] = val
    return val 
def fact(n:int) -> int:
    prod:int = 1
    for i in range(1,n+1):
        prod*=i
    return prod
a:float = float(input("a: "))
d:float = float(input("d: "))
N:int = int(input("N: "))
prod:float = a**N + fact(N-1)*a*(d**(N-1)) + sum([S(j,N-1)*(a**(N-j)*(d**j)) for j in range(1,N-2+1)])
print(f'Product: {prod}')
