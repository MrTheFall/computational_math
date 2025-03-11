import random

def create_matrix_from_keyboard():
    while True:
        print("Введите размер матрицы (количество строк):")
        size_input = input().strip()
        try:
            size = int(size_input)
            if size <= 0:
                print("Размер должен быть положительным целым числом. Попробуйте снова.")
                continue
            break
        except ValueError:
            print("Неверный формат числа. Введите целое число.")
    
    matrix = []
    expected_elements = size + 1
    print(f"Введите строки матрицы, разделяя элементы пробелом (каждая строка должна содержать {expected_elements} элементов):")
    for i in range(size):
        while True:
            row_input = input().strip()
            elements = row_input.split()
            if len(elements) != expected_elements:
                print(f"Ожидается {expected_elements} элементов в строке. Вы ввели {len(elements)}. Попробуйте снова.")
                continue
            try:
                row = list(map(lambda x: float(x.replace(',', '.')), elements))
                matrix.append(row)
                break
            except ValueError:
                print("Обнаружены нечисловые элементы. Попробуйте снова.")
    return matrix

def read_matrix_from_file(path):
    matrix = []
    eps = None
    try:
        with open(path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print("Файл не найден.")
        return None, None
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None, None
    
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        elements = stripped_line.split()
        if not elements:
            continue
        try:
            row = list(map(float, elements))
        except ValueError:
            print(f"Ошибка: строка '{stripped_line}' содержит нечисловые данные.")
            return None, None
        if len(row) == 1:
            if eps is None:
                eps = row[0]
            else:
                print("Ошибка: эпсилон уже указан. Пропускаем лишние значения.")
        else:
            matrix.append(row)
    
    if not matrix:
        print("Ошибка: матрица пуста.")
        return None, None
    size = len(matrix)
    for row in matrix:
        if len(row) != size + 1:
            print(f"Ошибка: все строки матрицы должны содержать {size + 1} элементов (для матрицы {size}x{size} + вектор). Найдена строка с {len(row)} элементами.")
            return None, None
    return matrix, eps

def get_epsilon():
    while True:
        print("Введите точность (эпсилон):")
        eps_input = input().strip().replace(',', '.')
        try:
            eps = float(eps_input)
            if eps <= 0:
                print("Эпсилон должен быть положительным числом. Попробуйте снова.")
                continue
            return eps
        except ValueError:
            print("Неверный формат числа. Введите число, например 0.001 или 1e-5.")

def check_diagonal(matrix):
    size = len(matrix)
    for i in range(size):
        row_sum = sum(abs(matrix[i][j]) for j in range(size))
        diagonal = abs(matrix[i][i])
        if row_sum - diagonal >= diagonal:
            return False
    return True

def achieve_diagonal_dominance(matrix):
    size = len(matrix)

    used_rows = [False] * size
    reordered_matrix = []

    for i in range(size):
        max_diagonal_val = float('-inf')
        selected_row_index = -1

        for j in range(size):
            if not used_rows[j]:
                diagonal_candidate = abs(matrix[j][i])
                row_sum = sum(abs(matrix[j][k]) for k in range(size))
                
                if diagonal_candidate > row_sum - diagonal_candidate and diagonal_candidate > max_diagonal_val:
                    max_diagonal_val = diagonal_candidate
                    selected_row_index = j

        if selected_row_index == -1:
            print("Невозможно достичь диагонального преобладания.")
            return None

        used_rows[selected_row_index] = True
        reordered_matrix.append(matrix[selected_row_index])

    return reordered_matrix

def generate_random_matrix(size):
    matrix = []
    max_index = random.randint(0, size - 1)
    for i in range(size):
        row = [random.randint(0, 10) for _ in range(size)]
        row[max_index] = sum(row) + random.randint(1, 10)
        row.append(random.randint(0, 10))
        matrix.append(row)
        max_index = (max_index + 1) % size
    return matrix

def solve(matrix, eps):
    size = len(matrix)
    x = [0.0] * size
    iter_counter = 0
    
    eps_str = f"{eps:.10f}".rstrip('0').rstrip('.') if 'e' not in str(eps) else str(eps)
    if 'e' in eps_str:
        if 'e-' in eps_str:
            decimal_places = int(eps_str.split('e-')[1])
        else:
            decimal_places = 0
    elif '.' in eps_str:
        decimal_places = len(eps_str.split('.')[1])
    else:
        decimal_places = 0
    
    while True:
        iter_counter += 1
        new_x = []
        norma = 0.0
        for i in range(size):
            sum_ = sum(matrix[i][j] * x[j] for j in range(size) if j != i)
            new_xi = (matrix[i][size] - sum_) / matrix[i][i]
            new_x.append(new_xi)
            norma = max(norma, abs(new_xi - x[i]))
        x = new_x
        if norma <= eps:
            break
    
    format_str = f"{{:.{decimal_places}f}}"
    
    result = {
        'norm': f"{norma:.9f}",
        'iterations': iter_counter,
        'solution': [{'index': i+1, 'value': format_str.format(x[i])} for i in range(size)],
        'inaccuracy': [{'index': i+1, 'value': format_str.format(sum(matrix[i][j] * x[j] for j in range(size)) - matrix[i][size])} for i in range(size)]
    }
    return result

def main():
    while True:
        print("1. Ввод с клавиатуры\n2. Ввод с файла\n3. Сгенерировать случайную матрицу")
        choice = input("Выберите способ ввода: ").strip()
        if choice in ("1", "2", "3"):
            break
        print("Неверный выбор. Введите 1, 2 или 3.")
    
    matrix = None
    eps = None
    
    if choice == "1":
        matrix = create_matrix_from_keyboard()
        eps = get_epsilon()
    elif choice == "2":
        path = input("Имя файла: ").strip()
        matrix, eps = read_matrix_from_file(path)
        if matrix is None:
            return
        if eps is None:
            eps = get_epsilon()
    elif choice == "3":
        while True:
            print("Введите размер матрицы (количество строк):")
            size_input = input().strip()
            try:
                size = int(size_input)
                if size <= 0:
                    print("Размер должен быть положительным целым числом. Попробуйте снова.")
                    continue
                break
            except ValueError:
                print("Неверный формат числа. Введите целое число.")
        matrix = generate_random_matrix(size)
        for line in matrix:
            print(*line)
        eps = get_epsilon()
    
    if matrix is None or eps is None:
        return
    
    if not check_diagonal(matrix):
        print("Попытка перестановки строк для достижения диагонального преобладания...")
        matrix = achieve_diagonal_dominance(matrix)
        if matrix is None:
            print("Диагонального преобладания не удалось достичь.")
            return
    
    size = len(matrix)
    for i in range(size):
        if matrix[i][i] == 0:
            print("Ошибка: нулевой элемент на диагонали. Невозможно решить.")
            return

    result = solve(matrix, eps)
    if result is None:
        return
    
    print("Результат:")
    print(f"Норма: {result['norm']}")
    print(f"Количество итераций: {result['iterations']}")
    print("Решение:")
    for sol in result['solution']:
        print(f"x{sol['index']} = {sol['value']}")
    print("Невязки:")
    for inacc in result['inaccuracy']:
        print(f"delta x{inacc['index']} = {inacc['value']}")

if __name__ == "__main__":
    main()