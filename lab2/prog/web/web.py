from flask import Flask, render_template, request
import math
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

app = Flask(__name__)

def f1(x):
    return x**3 - 2*x - 5

def f1_prime(x):
    return 3*x**2 - 2

def f2(x):
    return math.exp(x) - 2*x - 2

def f2_prime(x):
    return math.exp(x) - 2

def f3(x):
    return math.sin(x) + 0.5

def f3_prime(x):
    return math.cos(x)

def f4(x):
    return x**2 - 2

def f4_prime(x):
    return 2*x

def has_root(f, a, b):
    return f(a) * f(b) < 0

def is_monotonic(f_prime, a, b):
    samples = int((b - a) // 0.1)
    step = (b - a) / samples
    signs = set()
    for i in range(samples + 1):
        x = a + i * step
        try:
            df = f_prime(x)
            signs.add(math.copysign(1, df))
            if len(signs) > 1:
                return False
        except Exception:
            continue
    return True

def analyze_interval(f, f_prime, a, b):
    if a > b:
        a, b = b, a
    if not has_root(f, a, b):
        return False, "На интервале нет корней"
    if not is_monotonic(f_prime, a, b):
        return True, "Внимание: возможно несколько корней!"
    return True, "Интервал корректен"

def chord_method(f, a, b, eps, max_iter=1000):
    fa, fb = f(a), f(b)
    iterations = 0
    for _ in range(max_iter):
        c = (a * fb - b * fa) / (fb - fa)
        fc = f(c)
        iterations += 1
        if abs(fc) < eps:
            return c, iterations
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    return (a + b) / 2, iterations

def newton_method(f, f_prime, x0, eps, max_iter=1000):
    x = x0
    for i in range(max_iter):
        fx = f(x)
        if abs(fx) < eps:
            return x, i + 1
        dfx = f_prime(x)
        if dfx == 0:
            raise ValueError("Производная равна нулю")
        x_new = x - fx / dfx
        if abs(x_new - x) < eps:
            return x_new, i + 1
        x = x_new
    return x, max_iter

def simple_iteration_method(f, f_prime, a, b, eps, max_iter=1000):
    df_a = abs(f_prime(a))
    df_b = abs(f_prime(b))
    max_df = max(df_a, df_b)
    
    if max_df == 0:
        raise ValueError("Производная на интервале равна нулю, метод неприменим")

    if f_prime(a) > 0 and f_prime(b) > 0:
        lambda_ = -1 / max_df
    elif f_prime(a) < 0 and f_prime(b) < 0:
        lambda_ = 1 / max_df
    else:
        raise ValueError("Производная меняет знак на интервале, метод может не сходиться")

    x_prev = (a + b) / 2.0
    for i in range(max_iter):
        x_new = x_prev + lambda_ * f(x_prev)
        if abs(x_new - x_prev) < eps:
            return x_new, i + 1
        x_prev = x_new
    
    return x_prev, max_iter


# Функции для систем нелинейных уравнений
systems = {
    "1": {
        'g1': lambda x, y: 0.3 - 0.1 * y**2,
        'g2': lambda x, y: 0.7 - 0.2 * x**2,
        'jacobian_norm': lambda x, y: max(0.2 * abs(y), 0.4 * abs(x)),
        'description': "\\begin{cases}x = 0.3 - 0.1y^2 \\\\ y = 0.7 - 0.2x^2 \\end{cases}"
    },
    "2": {
        'g1': lambda x, y: math.sin(y) / 3 + 0.5,
        'g2': lambda x, y: math.cos(x) / 2 - 0.2,
        'jacobian_norm': lambda x, y: max(abs(math.cos(y) / 3), abs(math.sin(x) / 2)),
        'description': "\\begin{cases}x = \\frac{\\sin(y)}{3} + 0.5 \\\\ y = \\frac{\\cos(x)}{2} - 0.2\\end{cases}"
    }
}

def simple_iteration_system(g1, g2, x0, y0, eps, max_iter=1000):
    iterations = 0
    x_prev, y_prev = x0, y0
    errors = []
    for _ in range(max_iter):
        x_new = g1(x_prev, y_prev)
        y_new = g2(x_prev, y_prev)
        iterations += 1
        dx = abs(x_new - x_prev)
        dy = abs(y_new - y_prev)
        errors.append((dx, dy))
        if dx < eps and dy < eps:
            return (x_new, y_new), iterations, errors
        x_prev, y_prev = x_new, y_new
    return (x_prev, y_prev), iterations, errors

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", systems=systems)

@app.route('/result', methods=['POST'])
def result():
    task_type = request.form.get("task_type")
    result_data = {}

    if task_type == "1":
        func_choice = request.form.get("function_choice")
        try:
            a = float(request.form.get("a"))
            b = float(request.form.get("b"))
            eps = float(request.form.get("eps"))
        except ValueError:
            result_data['error'] = "Некорректный ввод числовых значений."
            return render_template("result.html", result=result_data)

        funcs = {
            "1": (f1, f1_prime),
            "2": (f2, f2_prime),
            "3": (f3, f3_prime),
            "4": (f4, f4_prime)
        }
        f, f_prime = funcs[func_choice]
        valid, analysis_message = analyze_interval(f, f_prime, a, b)
        result_data['analysis_message'] = analysis_message

        if not valid:
            result_data['error'] = "Анализ интервала не прошёл: " + analysis_message
        else:
            try:
                chord_root, chord_iters = chord_method(f, a, b, eps)
                result_data['chord'] = {
                    "root": chord_root,
                    "iterations": chord_iters,
                    "f_value": f(chord_root)
                }
            except Exception as e:
                result_data['chord_error'] = str(e)

            try:
                x0 = (a + b) / 2
                newton_root, newton_iters = newton_method(f, f_prime, x0, eps)
                result_data['newton'] = {
                    "root": newton_root,
                    "iterations": newton_iters,
                    "f_value": f(newton_root)
                }
            except Exception as e:
                result_data['newton_error'] = str(e)

            try:
                simple_root, simple_iters = simple_iteration_method(f, f_prime, a, b, eps)
                result_data['simple_iteration'] = {
                    "root": simple_root,
                    "iterations": simple_iters,
                    "f_value": f(simple_root)
                }
            except Exception as e:
                result_data['simple_iteration_error'] = str(e)

        if not result_data.get('error'):
            try:
                xs = np.linspace(a, b, 400)
                ys = [f(x) for x in xs]
                
                fig, ax = plt.subplots()
                ax.plot(xs, ys, label="f(x)")
                ax.axhline(0, color='black', linewidth=0.5)
                ax.axvline(0, color='black', linewidth=0.5)
                ax.set_xlabel('x')
                ax.set_ylabel('f(x)')
                ax.set_title('График функции на интервале от {} до {}'.format(a, b))
                ax.legend()
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close(fig)
                
                result_data['plot'] = plot_data
            except Exception as e:
                result_data['plot_error'] = str(e)

    elif task_type == "2":
        system_choice = request.form.get("system_choice")
        try:
            x0 = float(request.form.get("x0"))
            y0 = float(request.form.get("y0"))
            eps = float(request.form.get("eps_system"))
        except ValueError:
            result_data['error'] = "Некорректный ввод числовых значений."
            return render_template("result.html", result=result_data)

        system = systems.get(system_choice)
        if not system:
            result_data['error'] = "Некорректный выбор системы."
        else:
            jacobian_norm = system['jacobian_norm'](x0, y0)
            result_data['jacobian_norm'] = jacobian_norm
            if jacobian_norm >= 1:
                result_data['jacobian_warning'] = "Предупреждение: достаточное условие сходимости не выполнено (норма >= 1)."
            else:
                result_data['jacobian_warning'] = "Достаточное условие сходимости выполнено (норма < 1)."
            try:
                (x, y), iterations, errors = simple_iteration_system(system['g1'], system['g2'], x0, y0, eps)
                result_data['system'] = {
                    "x": x,
                    "y": y,
                    "iterations": iterations,
                    "errors": errors
                }
                f1_val = x - system['g1'](x, y)
                f2_val = y - system['g2'](x, y)
                result_data['check'] = {
                    "f1": f1_val,
                    "f2": f2_val
                }
            except Exception as e:
                print(e)
                result_data['system_error'] = 'Не удалость решить систему'

        if not result_data.get('system_error'):
            try:
                x_sol = result_data['system']['x']
                y_sol = result_data['system']['y']
                margin = 5.0
                
                y_values = np.linspace(y_sol - margin, y_sol + margin, 400)
                x_values_curve1 = [system['g1'](x_sol, y) for y in y_values]
                
                x_values = np.linspace(x_sol - margin, x_sol + margin, 400)
                y_values_curve2 = [system['g2'](x, y_sol) for x in x_values]
                
                fig, ax = plt.subplots()
                ax.plot(x_values_curve1, y_values, label="x = g₁(y)")
                ax.plot(x_values, y_values_curve2, label="y = g₂(x)")
                ax.plot(x_sol, y_sol, 'ro', label="Решение")
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.set_title('График системы')
                ax.legend()
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                system_plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close(fig)
                
                result_data['system_plot'] = system_plot_data
            except Exception as e:
                result_data['system_plot_error'] = str(e)

    else:
        result_data['error'] = "Некорректный выбор типа задачи."

    return render_template("result.html", result=result_data)

if __name__ == "__main__":
    app.run(debug=True)
