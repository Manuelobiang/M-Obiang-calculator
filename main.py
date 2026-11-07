# ============================================================
# M OBIANG CALCULATOR 3.0
# Windows 10 | Python 3.9+ | CustomTkinter + Tkinter
# ============================================================
# Dependencia visual:
#   py -m pip install customtkinter
#
# Ejecutar:
#   py main.py
#
# Nota matemática:
# - Ecuaciones lineales y cuadráticas: solución analítica.
# - Sistemas 2x2 y 3x3: eliminación de Gauss.
# - Otros tipos: búsqueda numérica aproximada de raíces reales.
# - La graficadora usa Canvas de Tkinter; no necesita matplotlib.
# ============================================================

import ast
import math
import cmath
import operator
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime

try:
    import customtkinter as ctk
except ImportError:
    raise SystemExit(
        "Falta CustomTkinter.\n"
        "Abre CMD y ejecuta: py -m pip install customtkinter"
    )

APP_NAME = "M OBIANG CALCULATOR"
VERSION = "3.0"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#101218"
SIDEBAR = "#151923"
PANEL = "#1B2130"
PANEL_ALT = "#20283A"
ACCENT = "#7187FF"
ACCENT_HOVER = "#5D72E8"
TEXT = "#F3F5FA"
MUTED = "#9AA4B8"
GREEN = "#48C9A0"
RED = "#F07885"
BORDER = "#30394B"

# ------------------------------------------------------------
# MOTOR MATEMÁTICO SEGURO
# ------------------------------------------------------------

FUNCTIONS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sqrt": math.sqrt, "abs": abs, "exp": math.exp,
    "log": math.log, "ln": math.log,
    "log10": math.log10, "log2": math.log2,
    "floor": math.floor, "ceil": math.ceil,
    "factorial": math.factorial,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
}
CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}
BIN_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.Mod: operator.mod,
}
UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def normalize_expression(expr):
    expr = expr.strip().replace("^", "**")
    expr = expr.replace("π", "pi").replace("÷", "/").replace("×", "*")
    expr = expr.replace("−", "-")
    return expr


def safe_eval(expr, variables=None):
    """Evalúa expresiones matemáticas sin ejecutar código Python arbitrario."""
    expr = normalize_expression(expr)
    variables = variables or {}
    tree = ast.parse(expr, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in variables:
                return variables[node.id]
            if node.id in CONSTANTS:
                return CONSTANTS[node.id]
            raise ValueError(f"Variable o constante desconocida: {node.id}")
        if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
            a, b = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(float(b)) > 1000:
                raise ValueError("Exponente demasiado grande.")
            result = BIN_OPS[type(node.op)](a, b)
            if isinstance(result, complex):
                if abs(result.imag) > 1e-10:
                    raise ValueError("El resultado no es real.")
                result = result.real
            if not math.isfinite(float(result)):
                raise ValueError("Resultado fuera del dominio numérico.")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
            return UNARY_OPS[type(node.op)](visit(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in FUNCTIONS or node.keywords:
                raise ValueError(f"Función no permitida: {name}")
            args = [visit(arg) for arg in node.args]
            if name in ("log", "ln") and len(args) == 2:
                return math.log(args[0], args[1])
            if len(args) != 1:
                raise ValueError(f"{name} necesita un argumento.")
            return FUNCTIONS[name](args[0])
        raise ValueError("Expresión no válida. Usa operaciones y funciones matemáticas.")

    return visit(tree)


def split_equation(text):
    if text.count("=") != 1:
        raise ValueError("Escribe una ecuación con un único signo =.")
    left, right = text.split("=")
    return normalize_expression(left), normalize_expression(right)


def equation_function(text):
    left, right = split_equation(text)
    return lambda x: float(safe_eval(left, {"x": x}) - safe_eval(right, {"x": x}))


def format_number(value):
    if isinstance(value, complex):
        if abs(value.imag) < 1e-10:
            value = value.real
        else:
            return f"{value.real:.8g} {'+' if value.imag >= 0 else '-'} {abs(value.imag):.8g}i"
    if isinstance(value, float):
        if abs(value - round(value)) < 1e-10:
            return str(int(round(value)))
        return f"{value:.10g}"
    return str(value)


def bisect_root(fn, a, b, iterations=90):
    fa, fb = fn(a), fn(b)
    if abs(fa) < 1e-10:
        return a
    if abs(fb) < 1e-10:
        return b
    if fa * fb > 0:
        raise ValueError("El intervalo no contiene un cambio de signo.")
    for _ in range(iterations):
        mid = (a + b) / 2
        fm = fn(mid)
        if abs(fm) < 1e-11 or abs(b - a) < 1e-11:
            return mid
        if fa * fm <= 0:
            b, fb = mid, fm
        else:
            a, fa = mid, fm
    return (a + b) / 2


def numerical_roots(fn, start=-100, end=100, steps=5000):
    roots = []
    last_x = start
    try:
        last_y = fn(last_x)
    except Exception:
        last_y = None

    for i in range(1, steps + 1):
        x = start + (end - start) * i / steps
        try:
            y = fn(x)
            if last_y is not None and math.isfinite(y) and math.isfinite(last_y):
                if abs(y) < 1e-8:
                    root = x
                elif last_y * y < 0:
                    root = bisect_root(fn, last_x, x)
                else:
                    root = None
                if root is not None and all(abs(root-r) > 1e-4 for r in roots):
                    roots.append(root)
        except Exception:
            pass
        last_x, last_y = x, None
        try:
            last_y = fn(x)
        except Exception:
            pass
    return sorted(roots)


def solve_equation(equation):
    left, right = split_equation(equation)
    fn = equation_function(equation)
    steps = [f"Ecuación original: {left} = {right}",
             f"Llevamos todos los términos al primer miembro: {left} - ({right}) = 0"]

    # Intento de extracción de polinomio de grado 1 o 2 mediante evaluación
    # de diferencias finitas; se valida en puntos adicionales.
    try:
        f0 = fn(0)
        f1 = fn(1)
        fm1 = fn(-1)
        a = (f1 + fm1 - 2*f0) / 2
        b = (f1 - fm1) / 2
        c = f0
        f2 = fn(2)
        fm2 = fn(-2)
        is_quadratic = abs((4*a + 2*b + c) - f2) < 1e-7
        is_quadratic &= abs((4*a - 2*b + c) - fm2) < 1e-7
        if is_quadratic:
            if abs(a) < 1e-10:
                if abs(b) < 1e-10:
                    if abs(c) < 1e-10:
                        return "Infinitas soluciones", steps + ["La igualdad se cumple para todo x del dominio."]
                    return "Sin solución", steps + ["Se obtiene una igualdad imposible."]
                root = -c / b
                steps += [f"Ecuación reducida: {format_number(b)}x + ({format_number(c)}) = 0",
                          f"Despejamos: x = -c/b = {format_number(root)}"]
                return f"x = {format_number(root)}", steps
            disc = b*b - 4*a*c
            steps += [f"Coeficientes: a = {format_number(a)}, b = {format_number(b)}, c = {format_number(c)}",
                      f"Discriminante: Δ = b² - 4ac = {format_number(disc)}"]
            if disc > 1e-10:
                r1 = (-b + math.sqrt(disc)) / (2*a)
                r2 = (-b - math.sqrt(disc)) / (2*a)
                steps += ["Aplicamos la fórmula general: x = (-b ± √Δ) / (2a)",
                          f"x₁ = {format_number(r1)}",
                          f"x₂ = {format_number(r2)}"]
                return f"x₁ = {format_number(r1)}\nx₂ = {format_number(r2)}", steps
            if abs(disc) <= 1e-10:
                r = -b/(2*a)
                steps += ["Δ = 0: existe una raíz doble.", f"x = {format_number(r)}"]
                return f"x = {format_number(r)} (raíz doble)", steps
            real = -b/(2*a)
            imag = math.sqrt(-disc)/(2*abs(a))
            steps += ["Δ < 0: no hay raíces reales.",
                      f"Raíces complejas: {format_number(complex(real, imag))} y {format_number(complex(real, -imag))}"]
            return f"{format_number(complex(real, imag))}\n{format_number(complex(real, -imag))}", steps
    except Exception:
        pass

    roots = numerical_roots(fn)
    steps.append("No se ha identificado una forma lineal o cuadrática sencilla.")
    steps.append("Se aplica búsqueda numérica de raíces reales en el intervalo [-100, 100].")
    if roots:
        steps += [f"Raíz aproximada {i+1}: x ≈ {format_number(r)}" for i, r in enumerate(roots)]
        return "\n".join(f"x{i+1} ≈ {format_number(r)}" for i, r in enumerate(roots)), steps
    return "No se encontraron raíces reales en [-100, 100].", steps + [
        "Puede haber raíces fuera del intervalo, raíces tangentes o soluciones complejas."
    ]


def solve_system(rows):
    """Resuelve sistemas lineales mediante eliminación de Gauss."""
    n = len(rows)
    matrix = [list(map(float, row)) for row in rows]
    if n not in (2, 3) or any(len(row) != n+1 for row in matrix):
        raise ValueError("El sistema debe ser 2x2 o 3x3.")
    steps = ["Matriz aumentada inicial:"]
    steps += [" | ".join(format_number(v) for v in row) for row in matrix]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(matrix[r][col]))
        if abs(matrix[pivot][col]) < 1e-12:
            raise ValueError("Sistema singular o con infinitas soluciones; no hay solución única.")
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        divisor = matrix[col][col]
        matrix[col] = [v/divisor for v in matrix[col]]
        for r in range(n):
            if r != col:
                factor = matrix[r][col]
                matrix[r] = [matrix[r][j] - factor*matrix[col][j] for j in range(n+1)]
        steps.append(f"Eliminación de Gauss, columna {col+1}:")
        steps += [" | ".join(format_number(v) for v in row) for row in matrix]

    solution = [matrix[i][-1] for i in range(n)]
    names = ["x", "y", "z"]
    result = "\n".join(f"{names[i]} = {format_number(solution[i])}" for i in range(n))
    steps.append("Solución obtenida:")
    steps.append(result)
    return result, steps


# ------------------------------------------------------------
# INTERFAZ
# ------------------------------------------------------------

class CalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {VERSION}")
        self.geometry("1240x790")
        self.minsize(1020, 680)
        self.configure(fg_color=BG)
        self.history = []
        self.current_page = None
        self._build_shell()
        self.show_page("Inicio")

    def _build_shell(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=238, corner_radius=0, fg_color=SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=22, pady=(28, 30))
        ctk.CTkLabel(brand, text="M", font=ctk.CTkFont("Arial", 30, "bold"),
                     text_color=ACCENT).pack(side="left")
        titlebox = ctk.CTkFrame(brand, fg_color="transparent")
        titlebox.pack(side="left", padx=10)
        ctk.CTkLabel(titlebox, text="OBIANG", font=ctk.CTkFont("Arial", 16, "bold"),
                     text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titlebox, text="CALCULATOR 3.0", font=ctk.CTkFont(size=9),
                     text_color=MUTED).pack(anchor="w")

        ctk.CTkLabel(self.sidebar, text="WORKSPACE", text_color="#657087",
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=24, pady=(0, 10))
        self.nav_buttons = {}
        pages = [
            ("Inicio", "⌂"), ("Básica y científica", "＋"),
            ("Ecuaciones", "ƒ"), ("Sistemas", "▦"),
            ("Graficadora", "⌁"), ("Historial", "◷"),
        ]
        for name, symbol in pages:
            btn = ctk.CTkButton(
                self.sidebar, text=f"  {symbol}    {name}", anchor="w",
                height=43, corner_radius=10, fg_color="transparent",
                hover_color=PANEL_ALT, text_color=MUTED,
                font=ctk.CTkFont(size=13),
                command=lambda n=name: self.show_page(n)
            )
            btn.pack(fill="x", padx=13, pady=3)
            self.nav_buttons[name] = btn

        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)
        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER).pack(fill="x", padx=18, pady=12)
        ctk.CTkLabel(self.sidebar, text="APPEARANCE", text_color="#657087",
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=24, pady=(0, 8))
        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar, values=["Oscuro", "Claro", "Sistema"],
            command=self.change_theme, fg_color=PANEL_ALT, button_color=ACCENT,
            height=34, corner_radius=9
        )
        self.theme_menu.pack(fill="x", padx=17, pady=(0, 20))
        ctk.CTkLabel(self.sidebar, text="M OBIANG  •  v3.0", text_color="#657087",
                     font=ctk.CTkFont(size=10)).pack(pady=(0, 15))

        self.main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.topbar = ctk.CTkFrame(self.main, fg_color=BG, corner_radius=0, height=72)
        self.topbar.grid(row=0, column=0, sticky="ew", padx=30)
        self.topbar.grid_columnconfigure(0, weight=1)
        self.page_title = ctk.CTkLabel(self.topbar, text="", text_color=TEXT,
                                       font=ctk.CTkFont(size=23, weight="bold"))
        self.page_title.grid(row=0, column=0, sticky="w", pady=23)
        self.clock_label = ctk.CTkLabel(self.topbar, text="MATHEMATICAL WORKSPACE",
                                        text_color=MUTED, font=ctk.CTkFont(size=10))
        self.clock_label.grid(row=0, column=1, sticky="e")

        self.content = ctk.CTkFrame(self.main, fg_color=BG, corner_radius=0)
        self.content.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 25))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Menú clásico de escritorio
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Guardar resultado como TXT", command=self.export_result)
        filemenu.add_separator()
        filemenu.add_command(label="Salir", command=self.destroy)
        menubar.add_cascade(label="Archivo", menu=filemenu)
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Inicio", command=lambda: self.show_page("Inicio"))
        viewmenu.add_command(label="Graficadora", command=lambda: self.show_page("Graficadora"))
        viewmenu.add_command(label="Historial", command=lambda: self.show_page("Historial"))
        menubar.add_cascade(label="Ver", menu=viewmenu)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Acerca de", command=self.about)
        menubar.add_cascade(label="Ayuda", menu=helpmenu)
        self.config(menu=menubar)

    def change_theme(self, value):
        ctk.set_appearance_mode({"Oscuro": "dark", "Claro": "light", "Sistema": "system"}[value])

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_page(self, name):
        self.current_page = name
        for page, btn in self.nav_buttons.items():
            btn.configure(fg_color=PANEL_ALT if page == name else "transparent",
                          text_color=TEXT if page == name else MUTED)
        self.page_title.configure(text=name)
        self.clear_content()
        {
            "Inicio": self.page_home,
            "Básica y científica": self.page_basic,
            "Ecuaciones": self.page_equations,
            "Sistemas": self.page_systems,
            "Graficadora": self.page_graph,
            "Historial": self.page_history,
        }[name]()

    def card(self, parent, title, subtitle=None):
        frame = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=16,
                             border_width=1, border_color=BORDER)
        if title:
            ctk.CTkLabel(frame, text=title, text_color=TEXT,
                         font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=19, pady=(17, 2))
        if subtitle:
            ctk.CTkLabel(frame, text=subtitle, text_color=MUTED,
                         font=ctk.CTkFont(size=11)).pack(anchor="w", padx=19, pady=(0, 12))
        return frame

    def add_history(self, operation, result):
        self.history.insert(0, (datetime.now().strftime("%H:%M:%S"), operation, result))

    def output_box(self, parent, height=190):
        box = ctk.CTkTextbox(parent, height=height, corner_radius=12,
                             fg_color="#111722", text_color="#DCE4F5",
                             border_width=1, border_color=BORDER,
                             font=ctk.CTkFont(family="Consolas", size=12),
                             wrap="word")
        return box

    def page_home(self):
        wrap = ctk.CTkFrame(self.content, fg_color="transparent")
        wrap.grid(row=0, column=0, sticky="nsew")
        wrap.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(wrap, text="Tu espacio de matemáticas.",
                     font=ctk.CTkFont(size=27, weight="bold"), text_color=TEXT).grid(
                         row=0, column=0, columnspan=2, sticky="w", pady=(14, 5))
        ctk.CTkLabel(wrap, text="Calcula, resuelve, analiza y representa funciones desde un solo lugar.",
                     text_color=MUTED, font=ctk.CTkFont(size=13)).grid(
                         row=1, column=0, columnspan=2, sticky="w", pady=(0, 24))
        modules = [
            ("01", "Calculadora científica", "Operaciones, potencias, raíces y trigonometría.", "Básica y científica"),
            ("02", "Ecuaciones", "Lineales, cuadráticas y resolución numérica.", "Ecuaciones"),
            ("03", "Sistemas lineales", "Sistemas de dos y tres incógnitas.", "Sistemas"),
            ("04", "Graficadora", "Representación visual de funciones y curvas.", "Graficadora"),
        ]
        for i, (num, title, desc, page) in enumerate(modules):
            r, col = 2 + i//2, i%2
            box = self.card(wrap, None)
            box.grid(row=r, column=col, sticky="nsew", padx=(0, 12) if col == 0 else (12, 0),
                     pady=9, ipady=10)
            ctk.CTkLabel(box, text=num, text_color=ACCENT,
                         font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(14, 8))
            ctk.CTkLabel(box, text=title, text_color=TEXT,
                         font=ctk.CTkFont(size=17, weight="bold")).pack(anchor="w", padx=20)
            ctk.CTkLabel(box, text=desc, text_color=MUTED, wraplength=390,
                         justify="left").pack(anchor="w", padx=20, pady=(6, 14))
            ctk.CTkButton(box, text="Abrir módulo  →", anchor="w", height=34,
                          fg_color=PANEL_ALT, hover_color=ACCENT_HOVER,
                          command=lambda p=page: self.show_page(p)).pack(
                              anchor="w", padx=20, pady=(0, 12))
        foot = self.card(wrap, "Motor matemático", "Las soluciones numéricas se identifican como aproximaciones.")
        foot.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ctk.CTkLabel(foot, text="Python · CustomTkinter · Tkinter Canvas · Sin conexión después de instalar la dependencia",
                     text_color=MUTED, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20, pady=(0, 17))

    def page_basic(self):
        wrap = ctk.CTkFrame(self.content, fg_color="transparent")
        wrap.grid(row=0, column=0, sticky="nsew")
        wrap.grid_columnconfigure(0, weight=3)
        wrap.grid_columnconfigure(1, weight=2)
        calc = self.card(wrap, "Calculadora", "Admite expresiones como 2*(5+3), sqrt(81), sin(pi/2), log(100,10).")
        calc.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        side = self.card(wrap, "Funciones disponibles", "Usa nombres en inglés para las funciones.")
        side.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        self.basic_entry = ctk.CTkEntry(calc, height=52, placeholder_text="Escribe una operación...",
                                        font=ctk.CTkFont(size=19), corner_radius=11)
        self.basic_entry.pack(fill="x", padx=19, pady=(10, 12))
        buttons = [
            ["7", "8", "9", "/", "sqrt("],
            ["4", "5", "6", "*", "^"],
            ["1", "2", "3", "-", "("],
            ["0", ".", "pi", "+", ")"],
            ["sin(", "cos(", "tan(", "log(", "ln("],
            ["asin(", "acos(", "atan(", "exp(", "abs("],
        ]
        grid = ctk.CTkFrame(calc, fg_color="transparent")
        grid.pack(fill="x", padx=17, pady=3)
        for r, line in enumerate(buttons):
            for col, value in enumerate(line):
                ctk.CTkButton(grid, text=value, height=39, corner_radius=9,
                              fg_color=PANEL_ALT, hover_color=ACCENT_HOVER,
                              command=lambda v=value: self.insert_basic(v)).grid(
                                  row=r, column=col, padx=3, pady=3, sticky="ew")
                grid.grid_columnconfigure(col, weight=1)
        actions = ctk.CTkFrame(calc, fg_color="transparent")
        actions.pack(fill="x", padx=19, pady=12)
        ctk.CTkButton(actions, text="Calcular", height=40, command=self.calculate_basic).pack(side="left")
        ctk.CTkButton(actions, text="Borrar", height=40, fg_color=PANEL_ALT,
                      command=lambda: self.basic_entry.delete(0, "end")).pack(side="left", padx=8)
        self.basic_result = ctk.CTkLabel(calc, text="Resultado: —", text_color=GREEN,
                                         font=ctk.CTkFont(size=18, weight="bold"))
        self.basic_result.pack(anchor="w", padx=20, pady=(5, 20))
        funcs = "sin(x), cos(x), tan(x)\nasin(x), acos(x), atan(x)\nsqrt(x), abs(x), exp(x)\nlog(x), ln(x), log10(x), log2(x)\n factorial(x), floor(x), ceil(x)\n\nConstantes: pi, e, tau\nPotencias: x^2 o x**2\nMultiplicación: 2*x"
        ctk.CTkLabel(side, text=funcs, justify="left", text_color=MUTED,
                     font=ctk.CTkFont(family="Consolas", size=12)).pack(anchor="w", padx=20, pady=15)

    def insert_basic(self, value):
        self.basic_entry.insert("insert", value)
        self.basic_entry.focus_set()

    def calculate_basic(self):
        expr = self.basic_entry.get()
        try:
            result = safe_eval(expr)
            text = format_number(result)
            self.basic_result.configure(text=f"Resultado: {text}")
            self.add_history(expr, text)
        except Exception as exc:
            messagebox.showerror("Error matemático", str(exc))

    def page_equations(self):
        wrap = ctk.CTkFrame(self.content, fg_color="transparent")
        wrap.grid(row=0, column=0, sticky="nsew")
        wrap.grid_columnconfigure(0, weight=1)
        left = self.card(wrap, "Solucionador de ecuaciones",
                         "Escribe la igualdad completa. Ejemplo: 2*x^2 - 5*x + 2 = 0")
        left.grid(row=0, column=0, sticky="ew")
        self.eq_entry = ctk.CTkEntry(left, height=48, placeholder_text="Ejemplo: x^2 - 5*x + 6 = 0",
                                     font=ctk.CTkFont(size=16))
        self.eq_entry.pack(fill="x", padx=20, pady=(5, 12))
        row = ctk.CTkFrame(left, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkButton(row, text="Resolver ecuación", height=40,
                      command=self.calculate_equation).pack(side="left")
        ctk.CTkButton(row, text="Ejemplo lineal", fg_color=PANEL_ALT,
                      command=lambda: self.set_eq("3*x + 5 = 20")).pack(side="left", padx=7)
        ctk.CTkButton(row, text="Ejemplo cuadrático", fg_color=PANEL_ALT,
                      command=lambda: self.set_eq("x^2 - 5*x + 6 = 0")).pack(side="left")
        coefrow = ctk.CTkFrame(left, fg_color="transparent")
        coefrow.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(coefrow, text="O introduce coeficientes (ax² + bx + c = 0):",
                     text_color=MUTED).pack(side="left", padx=(0, 10))
        self.coef_entries = []
        for label, default in (("a", "1"), ("b", "-5"), ("c", "6")):
            ctk.CTkLabel(coefrow, text=label, text_color=TEXT).pack(side="left", padx=(5, 3))
            ent = ctk.CTkEntry(coefrow, width=72, height=34, justify="center")
            ent.insert(0, default)
            ent.pack(side="left", padx=(0, 5))
            self.coef_entries.append(ent)
        ctk.CTkButton(coefrow, text="Resolver coeficientes", height=34,
                      fg_color=PANEL_ALT, command=self.calculate_coeff_equation).pack(side="left", padx=6)
        result_card = self.card(wrap, "Resultado y procedimiento",
                                "Las raíces de ecuaciones no polinómicas pueden ser aproximadas.")
        result_card.grid(row=1, column=0, sticky="nsew", pady=14)
        self.eq_output = self.output_box(result_card, 300)
        self.eq_output.pack(fill="both", expand=True, padx=18, pady=(5, 18))
        ctk.CTkLabel(wrap, text="Sintaxis: 2*x · x^2 · sqrt(x) · exp(x) · ln(x) · log(x,10) · sin(x)",
                     text_color=MUTED, font=ctk.CTkFont(size=11)).grid(row=2, column=0, sticky="w")

    def set_eq(self, value):
        self.eq_entry.delete(0, "end")
        self.eq_entry.insert(0, value)

    def calculate_coeff_equation(self):
        try:
            a, b, c = [float(entry.get()) for entry in self.coef_entries]
            if abs(a) < 1e-12:
                if abs(b) < 1e-12:
                    raise ValueError("a y b no pueden ser ambos cero.")
                result = f"x = {format_number(-c/b)}"
                steps = ["Forma lineal: bx + c = 0", f"x = -c/b = {format_number(-c/b)}"]
            else:
                equation = f"({a})*x^2 + ({b})*x + ({c}) = 0"
                result, steps = solve_equation(equation)
            self.eq_output.delete("1.0", "end")
            self.eq_output.insert("end", "SOLUCIÓN POR COEFICIENTES\n" + result + "\n\nPROCEDIMIENTO\n")
            self.eq_output.insert("end", "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps)))
            self.add_history("Coeficientes cuadráticos", result)
        except Exception as exc:
            messagebox.showerror("Coeficientes no válidos", str(exc))

    def calculate_equation(self):
        equation = self.eq_entry.get().strip()
        try:
            result, steps = solve_equation(equation)
            self.eq_output.delete("1.0", "end")
            self.eq_output.insert("end", "SOLUCIÓN\n" + result + "\n\nPROCEDIMIENTO\n")
            self.eq_output.insert("end", "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps)))
            self.add_history(equation, result)
        except Exception as exc:
            messagebox.showerror("No se pudo resolver", str(exc))

    def page_systems(self):
        wrap = ctk.CTkFrame(self.content, fg_color="transparent")
        wrap.grid(row=0, column=0, sticky="nsew")
        wrap.grid_columnconfigure(0, weight=1)
        card = self.card(wrap, "Sistemas de ecuaciones lineales",
                         "Introduce los coeficientes de cada ecuación y el término independiente.")
        card.grid(row=0, column=0, sticky="ew")
        selector = ctk.CTkFrame(card, fg_color="transparent")
        selector.pack(fill="x", padx=20, pady=(4, 10))
        self.system_size = tk.IntVar(value=2)
        ctk.CTkRadioButton(selector, text="2 incógnitas", variable=self.system_size,
                           value=2, command=self.rebuild_system_inputs).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(selector, text="3 incógnitas", variable=self.system_size,
                           value=3, command=self.rebuild_system_inputs).pack(side="left")
        self.system_inputs_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.system_inputs_frame.pack(fill="x", padx=20, pady=8)
        self.system_entries = []
        self.rebuild_system_inputs()
        ctk.CTkButton(card, text="Resolver sistema", height=42,
                      command=self.calculate_system).pack(anchor="w", padx=20, pady=(8, 17))
        outcard = self.card(wrap, "Solución y eliminación de Gauss")
        outcard.grid(row=1, column=0, sticky="nsew", pady=14)
        self.system_output = self.output_box(outcard, 270)
        self.system_output.pack(fill="both", expand=True, padx=18, pady=(5, 18))

    def rebuild_system_inputs(self):
        for w in self.system_inputs_frame.winfo_children():
            w.destroy()
        self.system_entries = []
        n = self.system_size.get()
        names = ["x", "y", "z"]
        for r in range(n):
            row = ctk.CTkFrame(self.system_inputs_frame, fg_color="transparent")
            row.pack(fill="x", pady=6)
            entries = []
            for c in range(n+1):
                ent = ctk.CTkEntry(row, width=105, height=39,
                                   placeholder_text="0", justify="center")
                ent.pack(side="left", padx=(0, 8))
                ent.insert(0, "1" if c == r else ("0" if c < n else str(r+1)))
                entries.append(ent)
                if c < n:
                    ctk.CTkLabel(row, text=names[c], text_color=MUTED).pack(side="left", padx=(0, 12))
                elif c == n:
                    ctk.CTkLabel(row, text="=", text_color=TEXT).pack(side="left", padx=(0, 10))
            self.system_entries.append(entries)

    def calculate_system(self):
        try:
            rows = [[float(e.get()) for e in row] for row in self.system_entries]
            result, steps = solve_system(rows)
            self.system_output.delete("1.0", "end")
            self.system_output.insert("end", "SOLUCIÓN\n" + result + "\n\nPROCEDIMIENTO\n")
            self.system_output.insert("end", "\n".join(steps))
            self.add_history("Sistema lineal", result)
        except Exception as exc:
            messagebox.showerror("Error en el sistema", str(exc))

    def page_graph(self):
        wrap = ctk.CTkFrame(self.content, fg_color="transparent")
        wrap.grid(row=0, column=0, sticky="nsew")
        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_rowconfigure(1, weight=1)
        controls = self.card(wrap, "Graficadora de funciones",
                             "Introduce una función de x. Ejemplo: sin(x), x^2 - 4 o exp(-x^2).")
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        bar = ctk.CTkFrame(controls, fg_color="transparent")
        bar.pack(fill="x", padx=18, pady=(2, 14))
        self.graph_entry = ctk.CTkEntry(bar, height=40, placeholder_text="f(x) = x^2",
                                        font=ctk.CTkFont(size=15))
        self.graph_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.graph_entry.insert(0, "x^2")
        ctk.CTkButton(bar, text="Graficar", height=40, command=self.draw_graph).pack(side="left")
        self.graph_canvas = tk.Canvas(wrap, bg="#111722", highlightthickness=1,
                                      highlightbackground=BORDER)
        self.graph_canvas.grid(row=1, column=0, sticky="nsew")
        self.graph_canvas.bind("<Configure>", lambda event: self.draw_graph())
        self.draw_graph()

    def draw_graph(self):
        if not hasattr(self, "graph_canvas") or not self.graph_canvas.winfo_exists():
            return
        canvas = self.graph_canvas
        canvas.delete("all")
        w = max(canvas.winfo_width(), 400)
        h = max(canvas.winfo_height(), 300)
        scale = 42
        ox, oy = w/2, h/2
        # cuadrícula
        for x in range(int(-ox/scale)-1, int(ox/scale)+2):
            px = ox + x*scale
            canvas.create_line(px, 0, px, h, fill="#222C3D")
            if x and x % 2 == 0:
                canvas.create_text(px+3, oy+12, text=str(x), fill="#8490A6", anchor="nw")
        for y in range(int(-oy/scale)-1, int(oy/scale)+2):
            py = oy - y*scale
            canvas.create_line(0, py, w, py, fill="#222C3D")
            if y and y % 2 == 0:
                canvas.create_text(ox+5, py+2, text=str(y), fill="#8490A6", anchor="nw")
        canvas.create_line(0, oy, w, oy, fill="#9BA8C0", width=2)
        canvas.create_line(ox, 0, ox, h, fill="#9BA8C0", width=2)
        canvas.create_text(w-18, oy-14, text="x", fill=TEXT)
        canvas.create_text(ox+14, 13, text="y", fill=TEXT)
        try:
            expr = self.graph_entry.get().strip()
            points, previous = [], None
            for px in range(w):
                x = (px-ox)/scale
                try:
                    y = float(safe_eval(expr, {"x": x}))
                    py = oy-y*scale
                    if math.isfinite(py) and abs(py) < h*4:
                        if previous is not None and abs(py-previous[1]) < h:
                            points.extend([previous[0], previous[1], px, py])
                        previous = (px, py)
                    else:
                        previous = None
                except Exception:
                    previous = None
            for i in range(0, len(points)-3, 4):
                canvas.create_line(points[i], points[i+1], points[i+2], points[i+3],
                                   fill=ACCENT, width=2.5, smooth=True)
            canvas.create_text(15, 14, text=f"f(x) = {expr}", fill="#B8C5E3", anchor="nw")
        except Exception as exc:
            canvas.create_text(w/2, h/2, text=str(exc), fill=RED)

    def page_history(self):
        wrap = ctk.CTkFrame(self.content, fg_color="transparent")
        wrap.grid(row=0, column=0, sticky="nsew")
        wrap.grid_columnconfigure(0, weight=1)
        card = self.card(wrap, "Historial de operaciones", "Las operaciones de esta sesión aparecen aquí.")
        card.grid(row=0, column=0, sticky="nsew")
        self.history_box = self.output_box(card, 460)
        self.history_box.pack(fill="both", expand=True, padx=18, pady=(5, 12))
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 16))
        ctk.CTkButton(row, text="Actualizar", command=self.refresh_history).pack(side="left")
        ctk.CTkButton(row, text="Limpiar historial", fg_color="#743E4A",
                      hover_color="#8A4857", command=self.clear_history).pack(side="left", padx=8)
        self.refresh_history()

    def refresh_history(self):
        if not hasattr(self, "history_box") or not self.history_box.winfo_exists():
            return
        self.history_box.delete("1.0", "end")
        if not self.history:
            self.history_box.insert("end", "Todavía no hay operaciones.")
        for time, op, result in self.history:
            self.history_box.insert("end", f"[{time}]  {op}\n→ {result}\n\n")

    def clear_history(self):
        self.history.clear()
        self.refresh_history()

    def export_result(self):
        content = ""
        if hasattr(self, "eq_output") and self.eq_output.winfo_exists():
            content = self.eq_output.get("1.0", "end").strip()
        elif hasattr(self, "system_output") and self.system_output.winfo_exists():
            content = self.system_output.get("1.0", "end").strip()
        elif self.history:
            content = "\n\n".join(f"{t} | {op}\n{res}" for t, op, res in self.history)
        if not content:
            messagebox.showinfo("Exportar", "No hay resultados para guardar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Archivo de texto", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
            messagebox.showinfo("Exportar", "Resultado guardado correctamente.")

    def about(self):
        messagebox.showinfo(
            "Acerca de",
            f"{APP_NAME} {VERSION}\n\n"
            "Calculadora científica, solucionador de ecuaciones,\n"
            "sistemas lineales y graficadora.\n\n"
            "Desarrollada en Python con CustomTkinter y Tkinter."
        )


if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()
