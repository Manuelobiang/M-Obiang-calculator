# M OBIANG CALCULATOR 3.0

Calculadora de escritorio desarrollada en Python con CustomTkinter y Tkinter para Windows 10.

## Funciones

- Calculadora básica y científica.
- Operaciones con potencias, raíces, trigonometría y logaritmos.
- Resolución analítica de ecuaciones lineales y cuadráticas sencillas.
- Búsqueda numérica aproximada de raíces reales para otras ecuaciones.
- Sistemas lineales de 2 y 3 incógnitas mediante eliminación de Gauss.
- Graficadora de funciones con Tkinter Canvas.
- Historial de operaciones y exportación de resultados a TXT.
- Interfaz oscura con navegación por módulos.

## Requisitos

- Python 3.9 o superior.
- CustomTkinter.
- Tkinter (normalmente incluido en la instalación estándar de Python para Windows).

## Instalación en Windows

1. Instala Python desde https://www.python.org/downloads/ y marca **Add Python to PATH** durante la instalación.
2. Abre CMD en la carpeta del proyecto.
3. Instala la dependencia:

   ```bash
   py -m pip install -r requirements.txt
   ```

4. Ejecuta la aplicación:

   ```bash
   py main.py
   ```

## Uso rápido

- En **Básica y científica**, escribe expresiones como `sqrt(81)`, `sin(pi/2)` o `log(100,10)`.
- En **Ecuaciones**, escribe una igualdad, por ejemplo `x^2 - 5*x + 6 = 0`.
- En **Sistemas**, introduce los coeficientes de un sistema lineal 2x2 o 3x3.
- En **Graficadora**, escribe una función de `x`, por ejemplo `x^2 - 4` o `sin(x)`.

Usa `*` para multiplicar explícitamente: escribe `2*x`, no `2x`.
Las funciones trigonométricas trabajan en radianes.

## Alcance y precisión matemática

Esta versión es una primera versión funcional y educativa; no es un sistema de álgebra computacional completo.

- Las ecuaciones lineales y cuadráticas sencillas se resuelven analíticamente.
- Los sistemas lineales 2x2 y 3x3 se resuelven mediante eliminación de Gauss.
- Para otras ecuaciones se buscan raíces reales numéricamente dentro del intervalo `[-100, 100]`.
- El método numérico puede no detectar raíces fuera de ese intervalo, raíces tangentes al eje o soluciones complejas.
- La graficadora dibuja la función en una ventana visible y puede omitir discontinuidades o zonas fuera de escala.

Comprueba los resultados importantes con otro método antes de utilizarlos en trabajos o cálculos de alta precisión.

## Estructura del proyecto

```text
M-OBIANG-CALCULATOR/
├── main.py
├── README.md
├── requirements.txt
└── LICENSE
```

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE`.

## Autor

M OBIANG
