import math
import sys


class Function:
    def __init__(self, name, func, discontinuity=None, symmetric=False):
        self.name = name
        self.func = func
        self.discontinuity = discontinuity
        self.symmetric = symmetric

    def calculate(self, x):
        return self.func(x)


class Integral:
    def __init__(self, name, antiderivative):
        self.name = name
        self.antiderivative = antiderivative

    def calculate(self, x):
        return self.antiderivative(x)


FUNCTION_1 = Function("f(x)=x^2", lambda x: x ** 2)
FUNCTION_2 = Function("f(x)=x^3", lambda x: x ** 3)
FUNCTION_3 = Function("f(x)=1/x", lambda x: 1 / x, discontinuity=0, symmetric=True)
FUNCTION_4 = Function("f(x)=1/(x+1)", lambda x: 1 / (x + 1), discontinuity=-1, symmetric=True)
FUNCTION_5 = Function("f(x)=1/(x^2)", lambda x: 1 / (x ** 2), discontinuity=0, symmetric=False)

INTEGRAL_1 = Integral("F(x)=x^3/3", lambda x: x ** 3 / 3)
INTEGRAL_2 = Integral("F(x)=x^4/4", lambda x: x ** 4 / 4)
INTEGRAL_3 = Integral("F(x)=ln|x|", lambda x: math.log(abs(x)) if x != 0 else 0)
INTEGRAL_4 = Integral("F(x)=ln|x+1|", lambda x: math.log(abs(x + 1)) if x != -1 else 0)
INTEGRAL_5 = Integral("F(x)=-1/x", lambda x: -1 / x if x != 0 else float('inf'))


def runge(curr_ans, prev_ans, order):
    return abs(curr_ans - prev_ans) / (order ** 2 - 1)


def mid_rectangle_method(func, a, b, n, tol):
    iterations = 0
    prev_ans = 0
    while True:
        step = (b - a) / n
        sum_val = 0
        for i in range(n):
            x_mid = a + (i + 0.5) * step
            sum_val += func.calculate(x_mid)
        curr_ans = step * sum_val
        iterations += 1
        if iterations > 1 and runge(curr_ans, prev_ans, 2) <= tol:
            break
        prev_ans = curr_ans
        n *= 2
        if iterations > 1000:
            break
    return curr_ans, iterations


def right_rectangle_method(func, a, b, n, tol):
    iterations = 0
    prev_ans = 0
    while True:
        step = (b - a) / n
        integral = sum(func.calculate(a + (i + 1) * step) for i in range(n))
        curr_ans = step * integral
        iterations += 1
        if iterations > 1 and runge(curr_ans, prev_ans, 2) <= tol:
            break
        prev_ans = curr_ans
        n *= 2
        if iterations > 1000:
            break
    return curr_ans, iterations


def left_rectangle_method(func, a, b, n, tol):
    iterations = 0
    prev_ans = 0
    while True:
        step = (b - a) / n
        integral = sum(func.calculate(a + i * step) for i in range(n))
        curr_ans = step * integral
        iterations += 1
        if iterations > 1 and runge(curr_ans, prev_ans, 2) <= tol:
            break
        prev_ans = curr_ans
        n *= 2
        if iterations > 1000:
            break
    return curr_ans, iterations


def trapezoidal_method(func, a, b, n, tol):
    iterations = 0
    prev_ans = 0
    while True:
        step = (b - a) / n
        integral = (func.calculate(a) + func.calculate(b)) / 2
        for i in range(1, n):
            x = a + i * step
            integral += func.calculate(x)
        curr_ans = step * integral
        iterations += 1
        if iterations > 1 and runge(curr_ans, prev_ans, 2) <= tol:
            break
        prev_ans = curr_ans
        n *= 2
        if iterations > 1000:
            break
    return curr_ans, iterations


def simpson_method(func, a, b, n, tol):
    iterations = 0
    prev_ans = 0
    while True:
        step = (b - a) / n
        integral = func.calculate(a) + func.calculate(b)
        for i in range(1, n):
            x = a + i * step
            if i % 2 == 0:
                integral += 2 * func.calculate(x)
            else:
                integral += 4 * func.calculate(x)
        curr_ans = step / 3 * integral
        iterations += 1
        if iterations > 1 and runge(curr_ans, prev_ans, 4) <= tol:
            break
        prev_ans = curr_ans
        n *= 2
        if iterations > 1000:
            break
    return curr_ans, iterations


def calculate_exact_integral(integ, a, b):
    return integ.calculate(b) - integ.calculate(a)


def calculate_integral(method, func, a, b, tol, n):
    total_method_iterations = 0
    prev_ans = 0
    while True:
        curr_ans, inner_iters = method(func, a, b, n, tol)
        total_method_iterations += inner_iters
        if n > 4 and abs(curr_ans - prev_ans) / 3 <= tol:
            break
        prev_ans = curr_ans
        n *= 2
        if n > 1000:
            break
    return curr_ans, total_method_iterations


def get_float(prompt, condition=lambda x: True, error_message="Неверный ввод."):
    while True:
        try:
            value = float(input(prompt).replace(',', '.'))
            if condition(value):
                return value
            else:
                print(error_message)
        except ValueError:
            print(error_message)


def main():
    functions_list = {
        1: (FUNCTION_1, INTEGRAL_1),
        2: (FUNCTION_2, INTEGRAL_2),
        3: (FUNCTION_3, INTEGRAL_3),
        4: (FUNCTION_4, INTEGRAL_4),
        5: (FUNCTION_5, INTEGRAL_5)
    }
    
    print("Доступные функции:")
    for num, (func_obj, integ_obj) in functions_list.items():
        print(f"{num}. {func_obj.name}  |  Точный интеграл: {integ_obj.name}")
    
    while True:
        try:
            s = int(input("Введите номер функции (1-5): "))
            if 1 <= s <= 5:
                break
            else:
                print("Номер функции должен быть в диапазоне от 1 до 5. Попробуйте еще раз.")
        except ValueError:
            print("Неверный формат ввода. Пожалуйста, введите целое число.")
    
    print("\nВведите интервал интегрирования [a, b] (требуется b > a):")
    a = get_float("Введите значение a: ", error_message="Введите корректное число.")
    b = get_float("Введите значение b: ", condition=lambda x: x > a, error_message="b должно быть больше a.")
    
    e = get_float("Введите точность (0 < e < 1): ", condition=lambda x: 0 < x < 1,
                  error_message="Точность должна быть числом в диапазоне (0, 1).")
    
    func, integ = functions_list[s]
    if func.discontinuity is not None:
        EPSILON = get_float("Введите значение отступа от разрыва: ", error_message="Введите корректное число.")
        if a == func.discontinuity:
            a += EPSILON
            print(f"Точка a совпадает с точкой разрыва. Установлено a = {a}")
        if b == func.discontinuity:
            b -= EPSILON
            print(f"Точка b совпадает с точкой разрыва. Установлено b = {b}")
    segments = []
    if func.discontinuity is not None and a < func.discontinuity < b:
        c = func.discontinuity
        if func.symmetric:
            delta = min(c - a, b - c)
            sym_left = c - delta
            sym_right = c + delta
            print(f"\nОбнаружен разрыв 2-го рода с симметрией относительно точки {c} на интервале [{sym_left}, {sym_right}].")
            print("Симметричный отрезок обнуляется при вычислении интеграла.")
            if sym_left > a:
                segments.append((a, sym_left))
            if b > sym_right:
                segments.append((sym_right, b))
        else:
            segments.append((a, c - EPSILON))
            segments.append((c + EPSILON, b))
    else:
        segments.append((a, b))
    accurate_integral_total = sum(calculate_exact_integral(integ, seg_a, seg_b) for seg_a, seg_b in segments)
    print(f"\nТочное значение интеграла: {accurate_integral_total}")
    n = 4
    methods_dict = {
        1: ("Метод средних прямоугольников", mid_rectangle_method, 2),
        2: ("Метод правых прямоугольников", right_rectangle_method, 2),
        3: ("Метод левых прямоугольников", left_rectangle_method, 2),
        4: ("Метод трапеций", trapezoidal_method, 2),
        5: ("Метод Симпсона", simpson_method, 4)
    }
    
    print("\nВыберите метод интегрирования (введите номер метода):")
    for num, (name, _, _) in methods_dict.items():
        print(f"{num}. {name}")
    print("6. Все методы")
    
    while True:
        try:
            method_num = int(input())
            if 1 <= method_num <= 6:
                break
            else:
                print("Введите число от 1 до 6.")
        except ValueError:
            print("Неверный формат ввода. Введите целое число.")
    if method_num != 6:
        method_name, method_func, order = methods_dict[method_num]
        integral_total = 0
        total_inner_iterations = 0
        for seg_a, seg_b in segments:
            result, inner_iters = calculate_integral(method_func, func, seg_a, seg_b, e, n)
            integral_total += result
            total_inner_iterations += inner_iters
        error = runge(integral_total, accurate_integral_total, order)
        print(f"\nРезультаты для метода: {method_name}")
        print(f"Значение интеграла: {integral_total}")
        print("Погрешность: {:.7f}%".format(error * 100))
        print(f"Количество итераций метода (внутренних циклов): {total_inner_iterations}")
    else:
        print("\nРезультаты для всех методов:")
        for num, (method_name, method_func, order) in methods_dict.items():
            integral_total = 0
            total_inner_iterations = 0
            for seg_a, seg_b in segments:
                result, inner_iters = calculate_integral(method_func, func, seg_a, seg_b, e, n)
                integral_total += result
                total_inner_iterations += inner_iters
            error = runge(integral_total, accurate_integral_total, order)
            print(f"\n{method_name}:")
            print(f"  Значение интеграла: {integral_total}")
            print("  Погрешность: {:.7f}%".format(error * 100))
            print(f"  Количество итераций метода (внутренних циклов): {total_inner_iterations}")


if __name__ == "__main__":
    while True:
        main()
        print('\n=================\n')
