import math


def calculate_mse(errors):
    """Расчет среднеквадратичного отклонения"""
    return sum(e * e for e in errors) / len(errors)


def calculate_pearson_correlation(x, y, coeffs=None):
    """Расчет коэффициента корреляции Пирсона"""
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    numerator = 0.0
    denominator_x = 0.0
    denominator_y = 0.0
    for xi, yi in zip(x, y):
        numerator += (xi - mean_x) * (yi - mean_y)
        denominator_x += (xi - mean_x) ** 2
        denominator_y += (yi - mean_y) ** 2
    return numerator / math.sqrt(denominator_x * denominator_y)


def fit_linear(x, y):
    """Линейная функция: y = a*x + b"""
    X = [[xi, 1.0] for xi in x]
    return solve_least_squares(X, y)


def fit_quadratic(x, y):
    """Полиномиальная функция 2-й степени: y = a*x^2 + b*x + c"""
    X = [[xi ** 2, xi, 1.0] for xi in x]
    return solve_least_squares(X, y)


def fit_cubic(x, y):
    """Полиномиальная функция 3-й степени: y = a*x^3 + b*x^2 + c*x + d"""
    X = [[xi ** 3, xi ** 2, xi, 1.0] for xi in x]
    return solve_least_squares(X, y)


def fit_exponential(x, y):
    """Экспоненциальная функция: y = a * exp(b*x)"""
    X = [[1.0, math.exp(xi)] for xi in x]
    y_log = [math.log(yi) for yi in y]
    coeffs = solve_least_squares(X, y_log)
    a = math.exp(coeffs[0])
    b = coeffs[1]
    return [a, b]


def fit_logarithmic(x, y):
    """Логарифмическая функция: y = a + b*ln(x)"""
    X = [[1.0, math.log(xi)] for xi in x]
    return solve_least_squares(X, y)


def fit_power(x, y):
    """Степенная функция: y = a * x^b"""
    X = [[1.0, math.log(xi)] for xi in x]
    y_log = [math.log(yi) for yi in y]
    coeffs = solve_least_squares(X, y_log)
    a = math.exp(coeffs[0])
    b = coeffs[1]
    return [a, b]


def solve_least_squares(X, y):
    Xt = transpose(X)
    XtX = multiply_matrix(Xt, X)
    XtY = multiply_matrix_vector(Xt, y)
    return solve_linear_system(XtX, XtY)


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def multiply_matrix(a, b):
    m, k = len(a), len(a[0])
    n = len(b[0])
    result = [[0.0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            for l in range(k):
                result[i][j] += a[i][l] * b[l][j]
    return result


def multiply_matrix_vector(matrix, vector):
    """Умножение матрицы на вектор"""
    m = len(matrix)
    n = len(matrix[0])
    result = [0.0] * m
    for i in range(m):
        for j in range(n):
            result[i] += matrix[i][j] * vector[j]
    return result


def solve_linear_system(A, b):
    """Решение системы линейных уравнений Ax = b методом Гаусса с выбором главного элемента"""
    n = len(A)
    M = [row[:] + [b_i] for row, b_i in zip(A, b)]

    # Прямой ход
    for i in range(n):
        max_row = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[max_row] = M[max_row], M[i]

        pivot = M[i][i]
        for j in range(i, n + 1):
            M[i][j] /= pivot
        for k in range(i + 1, n):
            factor = M[k][i]
            for j in range(i, n + 1):
                M[k][j] -= factor * M[i][j]

    # Обратный ход
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))
    return x