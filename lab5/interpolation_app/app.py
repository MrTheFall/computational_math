from flask import Flask, render_template, request
import base64
import io
import matplotlib.pyplot as plt
from interpolation_methods import (
    lagrange_polynomial,
    newton_divided_difference_polynomial,
    newton_finite_difference_polynomial,
    stirling_polynomial,
    bessel_polynomial,
    finite_differences
)
import math

app = Flask(__name__)

methods = [
    ('Лагранж', lagrange_polynomial),
    ('Ньютона с раздел. разн.', newton_divided_difference_polynomial),
    ('Ньютона с конечн. разност.', newton_finite_difference_polynomial),
    ('Стирлинг', stirling_polynomial),
    ('Бессель', bessel_polynomial),
]

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    data_text = request.form.get('data', '')
    x_input = request.form.get('x_input', '')
    try:
        x_val = float(x_input.replace(',', '.'))
    except ValueError:
        x_val = None
    points = []
    seen_xs = set()  # Track unique x-values
    for line in data_text.strip().splitlines():
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        try:
            x0 = float(parts[0].replace(',', '.'))
            y0 = float(parts[1].replace(',', '.'))
            if x0 not in seen_xs:  # Check for uniqueness
                points.append((x0, y0))
                seen_xs.add(x0)
        except ValueError:
            continue
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    results = []
    n = len(xs)
    # compute finite differences table for display
    try:
        delta_y = finite_differences(ys)
        # build a table where entries exist for i+j<n
        diff_table = []
        for i in range(n):
            row = []
            for j in range(n):
                if i + j < n:
                    row.append(delta_y[i][j])
                else:
                    row.append(None)
            diff_table.append(row)
    except Exception:
        diff_table = []
    if xs and ys and x_val is not None:
        # check uniform spacing for finite difference methods
        finite_difference = True
        if n > 1:
            last = xs[1] - xs[0]
            for i in range(1, n):
                new = abs(xs[i] - xs[i - 1])
                if abs(new - last) > 0.0001:
                    finite_difference = False
                last = new
        else:
            finite_difference = False
        # compute step and central index for t
        h = xs[1] - xs[0] if n > 1 else None
        alpha_ind = n // 2
        # filter methods and compute interpolation and t
        for name, func in methods:
            if func is newton_finite_difference_polynomial and not finite_difference:
                continue
            if func is newton_divided_difference_polynomial and finite_difference:
                continue
            # if (func is gauss_polynomial or func is stirling_polynomial) and len(xs) % 2 == 0:
            #     continue
            if func is bessel_polynomial and len(xs) % 2 == 1:
                continue
            # compute t for the method
            t = (x_val - xs[alpha_ind]) / h if h else None
            try:
                P = func(xs, ys, n)
                y_interp = P(x_val)
            except Exception:
                y_interp = None
            results.append({'name': name, 'value': y_interp, 't': t})
    # plot curves
    plot_url = None
    if xs and ys and x_val is not None and results:
        x_min, x_max = min(xs), max(xs)
        dx = (x_max - x_min) * 0.02 if x_max > x_min else 1
        x_vals = [x_min - dx + i * (x_max - x_min + 2*dx) / 500 for i in range(501)]
        plt.figure()
        for res in results:
            name = res['name']; P = dict(methods)[name]
            # get polynomial
            poly = P(xs, ys, n)
            y_vals = [poly(x) for x in x_vals]
            plt.plot(x_vals, y_vals, label=name)
        plt.scatter(xs, ys, color='black', label='Входные точки')
        if x_val is not None:
            plt.scatter([x_val], [results[0]['value']], color='red', label='Интерп. точка')
        plt.legend()
        plt.grid(True)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    # pass diff_table to template for finite differences
    return render_template('results.html', results=results, plot_url=plot_url, x_val=x_val, diff_table=diff_table)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')