from flask import Flask, render_template, request, redirect, url_for
import base64
import io
import matplotlib.pyplot as plt
import math
from approximation_methods import (
    fit_linear, fit_quadratic, fit_cubic,
    fit_exponential, fit_logarithmic, fit_power,
    calculate_mse, calculate_pearson_correlation
)

app = Flask(__name__)

models = [
    ('linear', fit_linear),
    ('quadratic', fit_quadratic),
    ('cubic', fit_cubic),
    ('exponential', fit_exponential),
    ('logarithmic', fit_logarithmic),
    ('power', fit_power),
]

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    data_text = request.form.get('data', '')
    best_only = request.form.get('best_only') == 'on'
    points = []
    for line in data_text.strip().splitlines():
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        try:
            # Поддержка запятой в дробных числах
            x_val = float(parts[0].replace(',', '.'))
            y_val = float(parts[1].replace(',', '.'))
            points.append((x_val, y_val))
        except ValueError:
            continue
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    results = []
    if ys:
        y_mean = sum(ys) / len(ys)
        for name, func in models:
            try:
                coeffs = func(xs, ys)
            except Exception:
                continue
            y_pred = []
            for x in xs:
                if name == 'linear':
                    a, b = coeffs; y_pred.append(a * x + b)
                elif name == 'quadratic':
                    a, b, c = coeffs; y_pred.append(a * x**2 + b * x + c)
                elif name == 'cubic':
                    a, b, c, d = coeffs; y_pred.append(a * x**3 + b * x**2 + c * x + d)
                elif name == 'exponential':
                    a, b = coeffs; y_pred.append(a * math.exp(b * x))
                elif name == 'logarithmic':
                    a, b = coeffs; y_pred.append(a + b * math.log(x) if x > 0 else float('nan'))
                elif name == 'power':
                    a, b = coeffs; y_pred.append(a * (x**b) if x > 0 else float('nan'))
            errors = [y - yp for y, yp in zip(ys, y_pred)]
            mse = calculate_mse(errors)
            ss_res = sum((y - yp)**2 for y, yp in zip(ys, y_pred))
            ss_tot = sum((y - y_mean)**2 for y in ys)
            r2 = 1 - ss_res / ss_tot if ss_tot != 0 else None
            pearson_r = calculate_pearson_correlation(xs, ys) if name == 'linear' else None
            # Определение достоверности аппроксимации
            if r2 is not None:
                if r2 >= 0.95:
                    reliability = 'Высокая точность аппроксимации (модель хорошо описывает явление)'
                elif r2 >= 0.75:
                    reliability = 'Удовлетворительная аппроксимация (модель в целом адекватно описывает явление)'
                elif r2 >= 0.5:
                    reliability = 'Слабая аппроксимация (модель слабо описывает явление)'
                else:
                    reliability = 'Точность аппроксимации недостаточна и модель требует изменения'
            else:
                reliability = None
            results.append({
                'name': name,
                'coeffs': coeffs,
                'mse': mse,
                'r2': r2,
                'reliability': reliability,
                'pearson_r': pearson_r,
                'data': list(zip(xs, ys, y_pred, errors))
            })
        # Фильтрация по лучшей модели, если запрошено
        if best_only and results:
            best = max(results, key=lambda r: r['r2'] if r['r2'] is not None else float('-inf'))
            results = [best]
    # Построение графика
    plot_url = None
    if xs and ys and results:
        x_min, x_max = min(xs), max(xs)
        delta = (x_max - x_min) * 0.1
        x_vals = [x_min - delta + i * (x_max - x_min + 2 * delta) / 500 for i in range(501)]
        plt.figure()
        for res in results:
            name = res['name']; coeffs = res['coeffs']
            y_vals = []
            for x in x_vals:
                if name == 'linear':
                    a, b = coeffs; y_vals.append(a * x + b)
                elif name == 'quadratic':
                    a, b, c = coeffs; y_vals.append(a * x**2 + b * x + c)
                elif name == 'cubic':
                    a, b, c, d = coeffs; y_vals.append(a * x**3 + b * x**2 + c * x + d)
                elif name == 'exponential':
                    a, b = coeffs; y_vals.append(a * math.exp(b * x))
                elif name == 'logarithmic':
                    a, b = coeffs; y_vals.append(a + b * math.log(x) if x > 0 else None)
                elif name == 'power':
                    a, b = coeffs; y_vals.append(a * (x**b) if x > 0 else None)
            plt.plot(x_vals, y_vals, label=name)
        plt.scatter(xs, ys, color='black', label='data')
        plt.legend()
        plt.grid(True)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    return render_template('results.html', results=results, plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')