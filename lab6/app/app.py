from flask import Flask, render_template, request
import math
import matplotlib
import matplotlib.pyplot as plt
import io, base64

app = Flask(__name__)

def linespace(start, end, num):
    if num <= 1:
        return [start]
    step = (end - start) / (num - 1)
    return [start + i * step for i in range(num)]

def euler(f, y0, x0, xn, h):
    n = int((xn - x0) / h)
    xs = linespace(x0, xn, n + 1)
    ys = [0.0] * (n + 1)
    ys[0] = y0
    for i in range(n):
        ys[i + 1] = ys[i] + h * f(xs[i], ys[i])
    return xs, ys

def improved_euler(f, y0, x0, xn, h):
    n = int((xn - x0) / h)
    xs = linespace(x0, xn, n + 1)
    ys = [0.0] * (n + 1)
    ys[0] = y0
    for i in range(n):
        k1 = f(xs[i], ys[i])
        k2 = f(xs[i] + h, ys[i] + h * k1)
        ys[i + 1] = ys[i] + h * (k1 + k2) / 2
    return xs, ys

def adams(f, y0, x0, xn, h, m=3):
    n = int((xn - x0) / h)
    xs = linespace(x0, xn, n + 1)
    ys = [0.0] * (n + 1)
    ys[0] = y0
    for i in range(m):
        ys[i + 1] = ys[i] + h * f(xs[i], ys[i])
    for i in range(m, n):
        y_pred = ys[i] + h * (
            55 * f(xs[i], ys[i])
            - 59 * f(xs[i - 1], ys[i - 1])
            + 37 * f(xs[i - 2], ys[i - 2])
            - 9 * f(xs[i - 3], ys[i - 3])
        ) / 24
        ys[i + 1] = ys[i] + h * (
            9 * f(xs[i + 1], y_pred)
            + 19 * f(xs[i], ys[i])
            - 5 * f(xs[i - 1], ys[i - 1])
            + f(xs[i - 2], ys[i - 2])
        ) / 24
    return xs, ys

def runge_error(method, f, y0, x0, xn, h, p):
    xs1, ys1 = method(f, y0, x0, xn, h)
    xs2, ys2 = method(f, y0, x0, xn, h / 2)
    return abs(ys1[-1] - ys2[-1]) / (2**p - 1)

def f1(x, y):
    return x - 2 * y

def f2(x, y):
    return x * y

def f3(x, y):
    return math.sin(x)

def f4(x, y):
    return y

def f5(x, y):
    return y * (1 - y)

def exact1(xs, x0, y0):
    C = (y0 - (x0/2 - 1/4))
    return [x/2 - 0.25 + C * math.exp(-2*(x - x0)) for x in xs]

def exact2(xs, x0, y0):
    return [y0 * math.exp((x**2 - x0**2)/2) for x in xs]

def exact3(xs, x0, y0):
    return [-math.cos(x) + y0 + math.cos(x0) for x in xs]

def exact4(xs, x0, y0):
    return [y0 * math.exp(x - x0) for x in xs]

def exact5(xs, x0, y0):
    return [1.0 / (1.0 + ((1 - y0)/y0) * math.exp(-(x - x0))) for x in xs]

ODES = {
    '1': (f1, 'x - 2*y', exact1),
    '2': (f2, 'x * y', exact2),
    '3': (f3, 'sin(x)', exact3),
    '4': (f4, 'y', exact4),
    '5': (f5, 'y*(1-y)', exact5)
}

METHODS = {
    'euler': (euler, 1, 'Метод Эйлера'),
    'improved': (improved_euler, 2, 'Усовершенствованный метод Эйлера'),
    'adams': (adams, 4, 'Метод Адамса')
}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    ode_key = request.form.get('ode')
    x0 = float(request.form.get('x0'))
    xn = float(request.form.get('xn'))
    n = int(request.form.get('n'))
    y0 = float(request.form.get('y0'))
    eps = float(request.form.get('eps'))
    method_key = request.form.get('method')

    if ode_key not in ODES or method_key not in METHODS:
        return 'Invalid selection', 400

    f, ode_str, exact = ODES[ode_key]
    method_func, p, method_name = METHODS[method_key]
    h = (xn - x0) / n

    xs, ys = method_func(f, y0, x0, xn, h)
    y_exact = exact(xs, x0, y0)
    if method_key in ('euler', 'improved'):
        error = runge_error(method_func, f, y0, x0, xn, h, p)
    else:
        error = max(abs(y_exact[i] - ys[i]) for i in range(len(ys)))

    plt.figure()
    plt.plot(xs, y_exact, linestyle='--', color='black', label='Точное решение')
    plt.plot(xs, ys, marker='o', label=method_name)
    plt.title(f"Решение ОДУ y' = {ode_str}")
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf8')
    plt.close()

    values = list(zip(xs, ys))
    return render_template('results.html', method_name=method_name,
                           ode_str=ode_str, error=error,
                           eps=eps, values=values,
                           plot_url=plot_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 
