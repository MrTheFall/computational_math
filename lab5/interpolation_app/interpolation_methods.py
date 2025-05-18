from copy import copy
from matplotlib import pyplot as plt

def factorial(n):
    res = 1
    for i in range(1, n+1):
        res *= i
    return res

def product(iterable):
    result = 1
    for item in iterable:
        result *= item
    return result

def lagrange_polynomial(xs, ys, n):
    return lambda x: sum([
        ys[i] * product(
            [(x - xs[j]) / (xs[i] - xs[j]) for j in range(n) if i != j]
        )
        for i in range(n)
    ])

def divided_differences(x, y):
    n = len(y)
    coef = [float(val) for val in y]
    for j in range(1, n):
        for i in range(n-1, j-1, -1):
            coef[i] = (coef[i] - coef[i-1]) / (x[i] - x[i-j])
    return coef

def newton_divided_difference_polynomial(xs, ys, n):
    coef = divided_differences(xs, ys)
    return lambda x: ys[0] + sum([
        coef[k] * product([x - xs[j] for j in range(k)]) for k in range(1, n)
    ])

def finite_differences(y):
    n = len(y)
    delta_y = [[0] * n for _ in range(n)]
    for i in range(n):
        delta_y[i][0] = y[i]
    for j in range(1, n):
        for i in range(n - j):
            delta_y[i][j] = delta_y[i+1][j-1] - delta_y[i][j-1]
    return delta_y

def newton_finite_difference_polynomial(xs, ys, n):
    h = xs[1] - xs[0]  # работает только для равноотстоящих узлов!
    delta_y = finite_differences(ys)
    return lambda x: ys[0] + sum(
        product([(x - xs[0]) / h - j for j in range(k)]) * delta_y[0][k] / factorial(k)
        for k in range(1, n)
    )

def stirling_polynomial(xs, ys, n):
    n = len(xs) - 1
    alpha_ind = n // 2
    fin_difs = [ys[:]]
    for k in range(1, n + 1):
        last = fin_difs[-1][:]
        fin_difs.append([last[i + 1] - last[i] for i in range(n - k + 1)])
    h = xs[1] - xs[0]
    dts1 = [((i+1)//2) * ((-1)**i) for i in range(n+1)]
    f1 = lambda x: ys[alpha_ind] + sum([
        product(
            [(x - xs[alpha_ind]) / h + dts1[j] for j in range(k)])
        * fin_difs[k][len(fin_difs[k]) // 2] / factorial(k)
        for k in range(1, n + 1)])
    f2 = lambda x: ys[alpha_ind] + sum([
        product(
            [(x - xs[alpha_ind]) / h - dts1[j] for j in range(k)])
        * fin_difs[k][len(fin_difs[k]) // 2 - (1 - len(fin_difs[k]) % 2)] / factorial(k)
        for k in range(1, n + 1)])
    return lambda x: (f1(x) + f2(x)) / 2

def bessel_polynomial(xs, ys, n):
    n = len(xs) - 1
    alpha_ind = n // 2
    fin_difs = [ys[:]]
    for k in range(1, n + 1):
        last = fin_difs[-1][:]
        fin_difs.append([last[i + 1] - last[i] for i in range(n - k + 1)])
    h = xs[1] - xs[0]
    
    dts1 = [((i+1)//2) * ((-1)**i) for i in range(n+1)]
    return lambda x: (ys[alpha_ind]) + sum([
        product(
            [(x - xs[alpha_ind]) / h + dts1[j] for j in range(k)])
        * fin_difs[k][len(fin_difs[k]) // 2] / factorial(2 * k) +
        ((x - xs[alpha_ind]) / h - 1 / 2) *
        product(
            [(x - xs[alpha_ind]) / h + dts1[j] for j in range(k)])
        * fin_difs[k][len(fin_difs[k]) // 2] / factorial(2 * k + 1)
        for k in range(1, n + 1)
    ])
